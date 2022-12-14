from sqlalchemy.orm import Session

from mmobot.db.models import Player, Zone
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id
from mmobot.utils.players import find_item_with_id, find_item_with_name


async def pickup_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) != 1:
        message = 'Please indicate what item you would like to pickup, for example: !pickup item'
        await context.send(message)
        return

    item_reference = args[0]
    discord_id = context.author.id
    with Session(engine) as session:
        player = Player.select_with_discord_id(session, discord_id)
        assert player is not None
        if player.hp == 0:
            message = f'<@{player.discord_id}> You are incapacitated.'
            await context.send(message)
            return

        zone = Zone.select_with_channel_id(session, context.channel.id)
        if is_entity_id(item_reference):
            item_id = convert_alphanum_to_int(item_reference)
            pickup_item = find_item_with_id(zone.loot, item_id)
        else:
            pickup_item = find_item_with_name(zone.loot, item_reference)
        if not pickup_item:
            await context.send(f'Could not find item to pick up: {item_reference}')
            return
        pickup_item.zone_id = None
        pickup_item.owner_id = player.id
        player.inventory_weight += pickup_item.item.weight
        session.commit()

        await context.send(f'You have picked up: {pickup_item.item.id}')
