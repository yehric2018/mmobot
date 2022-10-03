from sqlalchemy import select
from sqlalchemy.orm import Session


from mmobot.db.models import Player
from mmobot.utils.entities import convert_alphanum_to_int


async def equip_logic(zones, context, args, engine):
    if context.channel.name not in zones:
        return
    if len(args) != 1:
        message = 'Please indicate what item you would like to equip, for example: !equip item'
        await context.send(message)
        return

    item_reference = args[0]
    discord_id = context.author.id
    with Session(engine) as session:
        get_player_statement = (
            select(Player)
            .where(Player.discord_id == discord_id)
            .where(Player.is_active)
        )
        player = session.scalars(get_player_statement).one()
        if item_reference.startswith('/'):
            item_id = convert_alphanum_to_int(item_reference[1:])
            equipped_item = find_item_with_id(player.inventory, item_id)
        elif item_reference.isnumeric() and int(item_reference) < len(player.inventory):
            equipped_item = player.inventory[int(item_reference)]
        else:
            equipped_item = find_item_with_name(player.inventory, item_reference)
        if not equipped_item:
            await context.send(f'You do not have the item: {item_reference}')
        elif equipped_item.item.item_type == 'weapon':
            player.equipped_weapon_id = equipped_item.id
            session.commit()
            await context.send(f'You have equipped: {equipped_item.item.id}')
        else:
            await context.send(f'{equipped_item.name} cannot be equipped')


def find_item_with_id(inventory, numeric_id):
    for item_instance in inventory:
        if item_instance.id == numeric_id:
            return item_instance


def find_item_with_name(inventory, name):
    for item_instance in inventory:
        if item_instance.item.id == name:
            return item_instance
