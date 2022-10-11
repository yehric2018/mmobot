import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mmobot.db.models import Entity
from mmobot.db.models.minable import Minable

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


MINES_MINABLE_1 = Minable(
    zone='mines-entrance',
    title='Large minable rock wall',
    stone_comp=8000,
    coal_comp=2000,
    iron_comp=2500,
    silver_comp=500,
    gold_comp=100,
    diamond_comp=15,
    platinum_comp=1
)


INITIAL_ENTITIES = [
    MINES_MINABLE_1
]


def create_initial_entities():
    with Session(engine) as session:
        counter = 1

        for entity in INITIAL_ENTITIES:
            entity.id = counter
            session.add(entity)
            counter += 1

        session.commit()


# By default, the first 2000 entity IDs are reserved for initial entities.
def reset_initial_entities():
    with Session(engine) as session:
        delete_query = Entity.__table__.delete().where(Entity.id <= 2000)
        session.execute(delete_query)
        session.commit()


print('Deleting current initial entities...')
reset_initial_entities()
print('Reconstructing initial entities...')
create_initial_entities()
print('Done!')
