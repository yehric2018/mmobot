from sqlalchemy.orm import Session

from mmobot.db.models import Arrow, Attire, Bow, Player, Weapon
from mmobot.utils.entities import convert_alphanum_to_int, convert_int_to_alphanum, is_entity_id
from mmobot.utils.players import find_item_with_id, find_item_with_name


async def equip_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    discord_id = context.author.id
    if len(args) != 1:
        message = f'<@{discord_id}> Please indicate what item you would like to equip,'
        message += ' for example: !equip item'
        await context.send(message)
        return

    item_reference = args[0]
    with Session(engine) as session:
        player = Player.select_with_discord_id(session, discord_id)
        if player.hp == 0:
            message = f'<@{player.discord_id}> You are incapacitated.'
            await context.send(message)
            return
        if is_entity_id(item_reference):
            item_id = convert_alphanum_to_int(item_reference)
            equipped_item = find_item_with_id(player.inventory, item_id)
        else:
            equipped_item = find_item_with_name(player.inventory, item_reference)

        if not equipped_item:
            await context.send(f'<@{discord_id}> You do not have the item: {item_reference}')
            return

        reference = '/' + convert_int_to_alphanum(equipped_item.id)
        item_name = equipped_item.item.id
        if isinstance(equipped_item.item, Weapon):
            player.equipped_weapon_id = equipped_item.id
        elif isinstance(equipped_item.item, Attire):
            player.equipped_attire_id = equipped_item.id
        elif isinstance(equipped_item.item, Arrow):
            weapon = player.get_equipped_weapon()
            if weapon is None or not isinstance(weapon.item, Bow):
                message = f'<@{discord_id}> You must have a bow equipped first.'
                await context.send(message)
                return
            weapon.arrow_id = equipped_item.id
        else:
            message = f'<@{discord_id}> [ {reference} ] {item_name} cannot be equipped'
            await context.send(message)
            return
        await context.send(f'<@{discord_id}> You have equipped: [ {reference} ] {item_name}')
        session.commit()
