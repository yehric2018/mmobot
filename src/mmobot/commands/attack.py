from sqlalchemy import select
from sqlalchemy.orm import Session


from mmobot.db.models import Entity, Minable, Player
from mmobot.utils.battle import attack_command_pvp
from mmobot.utils.discord import is_mention
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id
from mmobot.utils.mining import attack_command_mining


async def attack_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) != 1:
        message = 'Please indicate a single attack target, for example: !attack target'
        await context.send(message)
        return

    if is_mention(args[0]):
        with Session(engine) as session:
            get_attacker_statement = (
                select(Player)
                .where(Player.discord_id == context.author.id)
                .where(Player.is_active)
            )
            attacker = session.scalars(get_attacker_statement).one()
            get_defender_statement = (
                select(Player)
                .where(Player.discord_id == args[0][2:-1])
                .where(Player.is_active)
            )
            defender = session.scalars(get_defender_statement).one_or_none()
            if defender is None:
                await context.send(f'Could not find target {args[0]}')
                return
            elif attacker == defender:
                await context.send('You cannot attack yourself!')
                return

            await attack_command_pvp(context, attacker, defender)
            session.commit()
        return

    if is_entity_id(args[0]):
        target_id = convert_alphanum_to_int(args[0][1:])
        with Session(engine) as session:
            get_player_statement = (
                select(Player)
                .where(Player.discord_id == context.author.id)
                .where(Player.is_active)
            )
            player = session.scalars(get_player_statement).one()

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
                return
    await context.send(f'Could not find target {args[0]}')
