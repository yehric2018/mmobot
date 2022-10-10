from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Player
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id
from mmobot.utils.players import find_item_with_id, find_item_with_name


async def drop_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) != 1:
        message = 'Please indicate what item you would like to drop, for example: !drop item'
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
        if is_entity_id(item_reference):
            item_id = convert_alphanum_to_int(item_reference)
            drop_item = find_item_with_id(player.inventory, item_id)
        elif item_reference.isnumeric() and int(item_reference) < len(player.inventory):
            drop_item = player.inventory[int(item_reference)]
        else:
            drop_item = find_item_with_name(player.inventory, item_reference)
        if not drop_item:
            await context.send(f'You do not have the item: {item_reference}')
            return
        drop_item.zone = zone_name
        drop_item.player_id = None
        if drop_item.id == player.equipped_weapon_id:
            player.equipped_weapon_id = None
        session.commit()

        await context.send(f'You have dropped: {drop_item.item.id}')
