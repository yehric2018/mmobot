import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import select

from mmobot.db.models import (
    Entity,
    Interaction,
    ItemInstance,
    Minable,
    Player,
    PlayerSkills,
    PlayerSkillTeaching,
    PlayerStats,
    WeaponInstance,
)


def init_test_engine():
    load_dotenv()
    MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
    MYSQL_DATABASE_NAME = os.getenv('MYSQL_TEST_DATABASE_NAME')

    connection_str = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
        MYSQL_USERNAME,
        MYSQL_PASSWORD,
        MYSQL_HOSTNAME,
        MYSQL_DATABASE_NAME
    )

    return create_engine(connection_str)


def add_to_database(session, database_entry):
    session.add(database_entry)
    session.commit()


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


def add_weapon_instance_to_zone(session, instance_id, zone_name, item_id):
    weapon_instance = WeaponInstance(
        id=instance_id,
        zone=zone_name,
        item_id=item_id
    )
    session.add(weapon_instance)
    session.commit()


def delete_all_entities(session):
    session.query(WeaponInstance).delete()
    session.query(ItemInstance).delete()
    session.query(Minable).delete()
    session.query(Interaction).delete()
    session.query(PlayerSkills).delete()
    session.query(PlayerSkillTeaching).delete()
    session.query(Player).delete()
    session.query(PlayerStats).delete()
    session.query(Entity).delete()
    session.commit()


def get_player_with_name(session, name):
    get_player_statement = select(Player).where(Player.name == name)
    return session.scalars(get_player_statement).one()


def get_player_skill_teachings(session, teacher_id, skill_name):
    get_teaching_statement = (
        select(PlayerSkillTeaching)
        .where(PlayerSkillTeaching.teacher == teacher_id)
        .where(PlayerSkillTeaching.skill == skill_name)
    )
    return session.scalars(get_teaching_statement).all()


def get_item_instance_with_id(session, id):
    get_item_statement = select(ItemInstance).where(ItemInstance.id == id)
    return session.scalars(get_item_statement).one()


def update_player(session, id, data):
    player = session.scalars(select(Player).where(Player.id == id)).one()
    if 'equipped_weapon_id' in data:
        player.equipped_weapon_id = data['equipped_weapon_id']
    if 'last_taught' in data:
        player.last_taught = data['last_taught']
    if 'zone' in data:
        player.zone = data['zone']
    session.commit()
