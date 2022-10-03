import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mmobot.constants import DB_ENTRY_SEPERATOR
from mmobot.db.models import Base, Item, Weapon, Zone, ZonePath

load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
if '--test' in sys.argv:
    MYSQL_DATABASE_NAME = os.getenv('MYSQL_TEST_DATABASE_NAME')
else:
    MYSQL_DATABASE_NAME = os.getenv('MYSQL_DATABASE_NAME')

connection_str = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
    MYSQL_USERNAME,
    MYSQL_PASSWORD,
    MYSQL_HOSTNAME,
    MYSQL_DATABASE_NAME
)
engine = create_engine(connection_str)


def setup():
    setup_zones()
    setup_items()


def setup_zones():
    all_zones = []
    all_zone_paths = []
    with open(os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'static', 'zones.db'), 'r') as f:
        file_text = f.read()
        zone_data = file_text.split(DB_ENTRY_SEPERATOR)
        for data in zone_data:
            all_zones.append(Zone(channel_name=data))

    zone_paths_path = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'static', 'zone-paths.db')
    with open(zone_paths_path, 'r') as f:
        file_text = f.read()
        zone_data = file_text.split(DB_ENTRY_SEPERATOR)
        for data in zone_data:
            lines = data.split('\n')
            zone_path = ZonePath(
                start_zone_name=lines[0],
                end_zone_name=lines[1],
                distance=int(lines[2]),
                guardable='G' in lines[3],
                lockable='L' in lines[3]
            )
            all_zone_paths.append(zone_path)

    with Session(engine) as session:
        for zone in all_zones:
            session.merge(zone)
        for zone_path in all_zone_paths:
            session.merge(zone_path)
        session.commit()


def setup_items():
    items_path = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'static', 'items.db')
    with open(os.path.join(items_path), 'r') as f:
        file_text = f.read()
        item_data = file_text.split(DB_ENTRY_SEPERATOR)
        all_items = []
        for data in item_data:
            lines = data.split('\n')
            item_stats = lines[1].split(',')

            all_items.append(Item(
                id=lines[0],
                size=int(item_stats[0]),
                weight=int(item_stats[1])
            ))

        with Session(engine) as session:
            for item in all_items:
                session.merge(item)
            session.commit()
    setup_weapons()


def setup_weapons():
    weapons_path = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'static', 'weapons.db')
    with open(os.path.join(weapons_path), 'r') as f:
        file_text = f.read()
        weapon_data = file_text.split(DB_ENTRY_SEPERATOR)
        all_weapons = []
        for data in weapon_data:
            lines = data.split('\n')
            item_stats = lines[2].split(',')

            weapon = Weapon(
                id=lines[0],
                item_type='weapon',
                size=int(item_stats[0]),
                weight=int(item_stats[1]),
                weapon_type=lines[1],
                strength=int(lines[3])
            )
            all_weapons.append(weapon)

        with Session(engine) as session:
            for weapon in all_weapons:
                session.merge(weapon)
            session.commit()


Base.metadata.create_all(engine)
setup()
