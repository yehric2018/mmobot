import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mmobot.constants import STANCE_NORMAL
from mmobot.db.models import Player
from mmobot.utils.players import roll_initial_stats

load_dotenv()
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_DATABASE_NAME = os.getenv('MYSQL_TEST_DATABASE_NAME')

engine = create_engine(f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}/{MYSQL_DATABASE_NAME}')

with Session(engine) as session:
    new_player = Player(
        name='Kelsier',
        discord_id='395341154071347220',
        ancestry=1,
        is_active=True,
        stance=STANCE_NORMAL,
        stats=roll_initial_stats()
    )

    session.add(new_player)

    session.commit()
