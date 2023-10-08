from sqlalchemy.orm import Session

from mmobot.constants import ATTACK_ENDURANCE_COST
from mmobot.db.models import Entity, MonsterInstance, Player
from mmobot.utils.battle import attack_in_channel
from mmobot.utils.discord import is_mention
from mmobot.utils.entities import is_entity_id
from mmobot.utils.players import kill_player


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
            elif player.endurance < ATTACK_ENDURANCE_COST + player.get_burden():
                message = f'<@{player.discord_id}> You do not have enough endurance.'
                await context.send(message)
                return

            await attack_in_channel(context.channel, player, defender)
            session.commit()
            if player.hp <= 0:
                kill_player(player.discord_id, engine, bot)
            if defender.hp <= 0:
                kill_player(defender.discord_id, engine, bot)
            return

        if is_entity_id(args[0]):
            target = Entity.select_with_reference(session, args[0], channel_id=context.channel.id)
            if target is None:
                await context.send(f'Could not find target {args[0]}')
                return

            if isinstance(target, MonsterInstance):
                await attack_in_channel(context.channel, player, target)
                session.commit()
                if target.hp <= 0:
                    await context.send(f'{target.get_name()} has been slain!')
                    target.kill()
                return
        await context.send(f'Could not find target {args[0]}')
