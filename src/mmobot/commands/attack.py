from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Entity, Minable, Player
from mmobot.utils.battle import attack_command_pvp
from mmobot.utils.discord import is_mention
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id
from mmobot.utils.mining import attack_command_mining
from mmobot.utils.players import handle_incapacitation, kill_player


async def attack_logic(bot, context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) != 1:
        message = 'Please indicate a single attack target, for example: !attack target'
        await context.send(message)
        return

    with Session(engine) as session:
        get_player_statement = (
            select(Player)
            .where(Player.discord_id == context.author.id)
            .where(Player.is_active)
        )
        player = session.scalars(get_player_statement).one()
        if player.stats.hp == 0:
            # The player is incapacitated, so nothing will happen.
            message = f'<@{player.discord_id}> You are incapacitated.'
            await context.send(message)
            return

        if is_mention(args[0]):
            get_defender_statement = (
                select(Player)
                .where(Player.discord_id == args[0][2:-1])
                .where(Player.is_active)
            )
            defender = session.scalars(get_defender_statement).one_or_none()
            if defender is None:
                await context.send(f'Could not find target {args[0]}')
                return
            elif player == defender:
                await context.send('You cannot attack yourself!')
                return
            elif defender.stats.hp == 0:
                await kill_player(defender.discord_id, engine, bot)
                return

            await attack_command_pvp(context, player, defender)
            session.commit()
            await handle_incapacitation(player, engine, bot)
            await handle_incapacitation(defender, engine, bot)
            return

        if is_entity_id(args[0]):
            target_id = convert_alphanum_to_int(args[0][1:])
            get_target_statement = (
                select(Entity)
                .where(Entity.id == target_id)
                .where(Entity.zone == context.channel.name)
            )
            target = session.scalars(get_target_statement).one()

            if target is None:
                await context.send(f'Could not find target {args[0]}')
                return
            if type(target) == Minable:
                await attack_command_mining(context, player, target, session)
                session.commit()
                await handle_incapacitation(player, engine, bot)
                return
        await context.send(f'Could not find target {args[0]}')
