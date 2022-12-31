import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mmobot.db.index import MonsterIndex
from mmobot.db.models import MonsterInstance, Zone

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_DATABASE_NAME = os.getenv('MYSQL_DATABASE_NAME')

connection_str = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
    MYSQL_USERNAME,
    MYSQL_PASSWORD,
    MYSQL_HOSTNAME,
    MYSQL_DATABASE_NAME
)

engine = create_engine(connection_str)

monster_index = MonsterIndex()


with Session(engine) as session:
    zone = Zone.select_with_channel_id(session, '1057913233727561858')
    monster = MonsterInstance.create_instance(monster_index.index['goblin'], zone=zone)
    monster.id = 12
    session.add(monster)

    session.commit()
