from sqlalchemy import select
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
    zone_name = context.channel.name
    with Session(engine) as session:
        get_player_statement = (
            select(Player)
            .where(Player.discord_id == discord_id)
            .where(Player.is_active)
        )
        player = session.scalars(get_player_statement).one()
        if player.hp == 0:
            message = f'<@{player.discord_id}> You are incapacitated.'
            await context.send(message)
            return

        get_zone_statement = (
            select(Zone)
            .where(Zone.channel_name == zone_name)
        )
        zone = session.scalars(get_zone_statement).one()
        if is_entity_id(item_reference):
            item_id = convert_alphanum_to_int(item_reference)
            pickup_item = find_item_with_id(zone.loot, item_id)
        else:
            pickup_item = find_item_with_name(zone.loot, item_reference)
        if not pickup_item:
            await context.send(f'Could not find item to pick up: {item_reference}')
            return
        pickup_item.zone = None
        pickup_item.player_id = player.id
        session.commit()

        await context.send(f'You have picked up: {pickup_item.item.id}')
