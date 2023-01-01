from sqlalchemy.orm import Session


from mmobot.db.models import BowInstance, Player
from mmobot.utils.entities import convert_int_to_alphanum, is_entity_id


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
        assert player is not None
        unequipped_item = None
        for item_instance in player.inventory:
            if ('/' + convert_int_to_alphanum(item_instance.id) == item_reference):
                unequipped_item = unequip_if_equipped(player, item_instance)
                break
            elif (item_instance.item.id == item_reference):
                unequipped_item = unequip_if_equipped(player, item_instance)
                if unequipped_item is not None:
                    break
        session.commit()

        if unequipped_item is not None:
            reference_id = '/' + convert_int_to_alphanum(unequipped_item[0])
            await context.send(f'Unequipped [ {reference_id} ] {unequipped_item[1]}')
        else:
            await context.send(f'{item_reference} is not equipped')


def unequip_if_equipped(player, item_instance):
    if player.equipped_weapon_id == item_instance.id:
        if isinstance(item_instance, BowInstance):
            item_instance.arrow = None
        player.equipped_weapon_id = None
    elif player.equipped_attire_id == item_instance.id:
        player.equipped_attire_id = None
    else:
        return None
    return (item_instance.id, item_instance.item.id)
