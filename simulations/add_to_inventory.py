import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import ArrowInstance, BowInstance, Player

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


with Session(engine) as session:
    get_player_statement = (
        select(Player)
        .where(Player.name == 'NoobLoser')
    )
    player = session.scalars(get_player_statement).one()
    
    player.inventory.append(BowInstance(item_id='wooden-bow'))
    player.inventory.append(ArrowInstance(item_id='stonehead-arrow'))
    player.inventory_weight += (5 + 1)

    session.commit()
