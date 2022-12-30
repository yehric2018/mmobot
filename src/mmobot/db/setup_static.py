import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mmobot.constants import DB_ENTRY_SEPERATOR
from mmobot.db.index import ItemIndex
from mmobot.db.models import (
    Attire,
    Base,
)

load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')
DATA_PATH = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'index', 'data')
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
    # TODO: Load in using MockItemIndex for tests so we don't need to load in as many  items
    item_index = ItemIndex()
    with Session(engine) as session:
        item_index.load_to_database(session)


def setup_attire():
    attire_path = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'index', 'attire.db')
    with open(os.path.join(attire_path), 'r') as f:
        file_text = f.read()
        attire_data = file_text.split(DB_ENTRY_SEPERATOR)
        all_attire = []
        for data in attire_data:
            lines = data.split('\n')
            item_stats = lines[1].split(',')
            armor_stats = lines[2].split(',')

            attire = Attire(
                id=lines[0],
                weight=float(item_stats[1]),
                coverage=int(armor_stats[0]),
                armor=int(armor_stats[1]),
                warmth=int(lines[3])
            )
            all_attire.append(attire)

        with Session(engine) as session:
            for attire in all_attire:
                session.merge(attire)
            session.commit()


Base.metadata.create_all(bind=engine)
setup()
