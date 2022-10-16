import os

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from mmobot.db.models import Player, PlayerStats

load_dotenv()
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

scheduler = BlockingScheduler()


@scheduler.scheduled_job(IntervalTrigger(minutes=5))
def recover_endurance():
    print('Recovering players\'s endurance')
    with Session(engine) as session:
        get_player_statement = (
            select(Player)
            .where(Player.is_active)
            .where(Player.stats.has(PlayerStats.endurance < PlayerStats.max_endurance))
        )
        for player in session.scalars(get_player_statement):
            player.stats.endurance += 1

        session.commit()


@scheduler.scheduled_job(IntervalTrigger(hours=2))
def recover_hp():
    print('Recovering players\'s HP')
    with Session(engine) as session:
        get_player_statement = (
            select(Player)
            .where(Player.is_active)
            .where(Player.stats.has(PlayerStats.hp < PlayerStats.hp))
        )
        for player in session.scalars(get_player_statement):
            player.stats.hp += 1

        session.commit()


@scheduler.scheduled_job(IntervalTrigger(hours=12))
def increment_skill_points():
    print('Allocating skill points')
    with Session(engine) as session:
        get_player_statement = select(Player).where(Player.is_active)
        for player in session.scalars(get_player_statement):
            player.skills.skill_points += 1

        session.commit()


print('Starting events bot...')
scheduler.start()
