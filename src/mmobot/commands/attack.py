from sqlalchemy.orm import Session

from mmobot.db.models import Entity, Minable, MonsterInstance, Player
from mmobot.utils.battle import attack_in_channel
from mmobot.utils.discord import is_mention
from mmobot.utils.entities import is_entity_id
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
        player = Player.select_with_discord_id(session, context.author.id)
        assert player is not None
        if player.hp == 0:
            message = f'<@{player.discord_id}> You are incapacitated.'
            await context.send(message)
            return

        if is_mention(args[0]):
            defender = Player.select_with_discord_id(
                session, args[0][2:-1], channel_id=context.channel.id
            )
            if defender is None:
                await context.send(f'Could not find target {args[0]}')
                return
            elif player == defender:
                await context.send('You cannot attack yourself!')
                return
            elif defender.hp == 0:
                await kill_player(defender.discord_id, engine, bot)
                return

            await attack_in_channel(context, player, defender)
            session.commit()
            await handle_incapacitation(player, engine, bot)
            await handle_incapacitation(defender, engine, bot)
            return

        if is_entity_id(args[0]):
            target = Entity.select_with_reference(session, args[0], channel_id=context.channel.id)
            if target is None:
                await context.send(f'Could not find target {args[0]}')
                return

            if isinstance(target, MonsterInstance):
                await attack_in_channel(context, player, target)
                session.commit()
                if target.hp <= 0:
                    await context.send(f'{target.get_name()} has been slain!')
                    target.kill()
                return
            elif isinstance(target, Minable):
                await attack_command_mining(context, player, target, session)
                session.commit()
                await handle_incapacitation(player, engine, bot)
                return
        await context.send(f'Could not find target {args[0]}')
