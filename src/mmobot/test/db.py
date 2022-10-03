from sqlalchemy import select

from mmobot.db.models import Entity, ItemInstance, Player, WeaponInstance


def add_item_instance(session, instance_id, player_id, item_id):
    item_instance = ItemInstance(
        id=instance_id,
        player_id=player_id,
        item_id=item_id
    )
    session.add(item_instance)
    session.commit()


def add_player(session, player):
    session.add(player)
    session.commit()


def add_weapon_instance(session, instance_id, player_id, item_id):
    weapon_instance = WeaponInstance(
        id=instance_id,
        player_id=player_id,
        item_id=item_id
    )
    session.add(weapon_instance)
    session.commit()


def delete_all_entities(session):
    session.query(WeaponInstance).delete()
    session.query(ItemInstance).delete()
    session.query(Player).delete()
    session.query(Entity).delete()
    session.commit()


def get_player_with_name(session, name):
    get_player_statement = select(Player).where(Player.name == name)
    return session.scalars(get_player_statement).one()


def get_item_instance_with_id(session, id):
    get_item_statement = select(ItemInstance).where(ItemInstance.id == id)
    return session.scalars(get_item_statement).one()


def update_player(session, id, data):
    player = session.scalars(select(Player).where(Player.id == id)).one()
    if 'equipped_weapon_id' in data:
        player.equipped_weapon_id = data['equipped_weapon_id']
    session.commit()
