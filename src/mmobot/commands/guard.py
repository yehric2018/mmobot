from sqlalchemy.orm import Session

from mmobot.db.models import Entity, Player
from mmobot.utils.discord import is_mention
from mmobot.utils.entities import is_entity_id


async def guard_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return

    with Session(engine) as session:
        player = Player.select_with_discord_id(session, context.author.id)
        assert player is not None
        if player.hp == 0:
            await context.send(f'<@{player.discord_id}> You are incapacitated.')
            return

        if len(args) == 0:
            player.guarding_entity_id = None
            await context.send(f'<@{player.discord_id}> You are no longer guarding.')
        elif is_mention(args[0]):
            guarded_player = Player.select_with_discord_id(
                session, args[0][2:-1], channel_id=context.channel.id
            )
            if guarded_player is None:
                message = f'<@{player.discord_id}> Could not find player in zone to guard.'
                await context.send(message)
                return
            player.guarding_entity_id = guarded_player.id
            await context.send(f'<@{player.discord_id}> is now guarding {args[0]}.')
        elif is_entity_id(args[0]):
            entity = Entity.select_with_reference(session, args[0], channel_id=context.channel.id)
            if entity is None:
                message = f'<@{player.discord_id}> Could not find {args[0]} to guard'
                await context.send(message)
                return
            player.guarding_entity_id = entity.id
            await context.send(f'<@{player.discord_id}> is now guarding {args[0]}.')
        else:
            message = f'<@{player.discord_id}> Please provide a mention or reference ID to guard.'
            await context.send(message)
            return
        session.commit()
