from sqlalchemy import select
from sqlalchemy.orm import Session


from mmobot.db.models import Player
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id


async def unequip_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) != 1:
        message = 'Please indicate which item you would like to unequip, '\
            'for example: !unequip item'
        await context.send(message)
        return
    item_reference = args[0]
    discord_id = context.author.id
    with Session(engine) as session:
        player = Player.select_with_discord_id(session, discord_id)

        did_unequip = False
        if is_entity_id(item_reference):
            did_unequip = unequip_using_id(player, convert_alphanum_to_int(item_reference))
        elif item_reference.isnumeric() and int(item_reference) < len(player.inventory):
            item_reference = player.inventory[int(item_reference)].item.id
            did_unequip = unequip_using_name(player, item_reference)
        else:
            did_unequip = unequip_using_name(player, item_reference)
        session.commit()

        if did_unequip:
            await context.send(f'Unequipped {item_reference}')
        else:
            await context.send(f'{item_reference} is not equipped')


def unequip_using_id(player, id):
    if player.equipped_weapon_id == id:
        player.equipped_weapon_id = None
        return True
    elif player.equipped_attire_id == id:
        player.equipped_attire_id = None
        return True
    return False


def unequip_using_name(player, name):
    for item_instance in player.inventory:
        if name == item_instance.item.id:
            if player.equipped_weapon_id == item_instance.id:
                player.equipped_weapon_id = None
                return True
            elif player.equipped_attire_id == item_instance.id:
                player.equipped_attire_id = None
                return True
    return False
