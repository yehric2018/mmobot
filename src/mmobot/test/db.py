from mmobot.db.models import Entity, ItemInstance, Player


def add_player(session, player):
    session.add(player)
    session.commit()


def add_item_instance(session, instance_id, player_id, item_id):
    item_instance = ItemInstance(
        id=instance_id,
        player_id=player_id,
        item_id=item_id
    )
    session.add(item_instance)
    session.commit()


def delete_all_entities(session):
    session.query(ItemInstance).delete()
    session.query(Player).delete()
    session.query(Entity).delete()
    session.commit()
