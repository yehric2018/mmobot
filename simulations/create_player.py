from datetime import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()

STANCE_NORMAL = 0
STANCE_BATTLE = 1
STANCE_GUARD = 2
STANCE_REST = 3
STANCE_SLEEP = 4

class Player(Base):
    __tablename__ = 'Players'

    name = Column(String(40), primary_key=True)
    discord_id = Column(String(40))
    ancestry = Column(Integer)
    birthday = Column(DateTime)
    parent_name = Column(String(40))
    is_active = Column(Boolean)
    stance = Column(Integer)
    hp = Column(Integer)
    max_hp = Column(Integer)
    armor = Column(Integer)
    mobility = Column(Integer)
    dexterity = Column(Integer)
    endurance = Column(Integer)
    max_endurance = Column(Integer)
    strength = Column(Integer)
    luck = Column(Integer)
    experience = Column(Integer)
    magic_number = Column(Integer)
    fighting_skill = Column(Integer)
    hunting_skill = Column(Integer)
    mining_skill = Column(Integer)
    cooking_skill = Column(Integer)
    crafting_skill = Column(Integer)
    equipped_weapon = Column(String(100))
    equipped_armor = Column(String(100))
    equipped_accessory = Column(String(100))
    guarding = Column(String(100))
    last_attack = Column(DateTime)

    def __repr__(self):
        return f'Player(nickname={self.nickname})'

class TestEntry(Base):
    __tablename__ = "TestTable"

    id = Column(Integer, primary_key=True)
    name = Column(String(20))

load_dotenv()
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_DATABASE_NAME = os.getenv('MYSQL_DATABASE_NAME')

engine = create_engine(f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}/{MYSQL_DATABASE_NAME}')
Base.metadata.create_all(engine)

with Session(engine) as session:
    new_player = Player(
        name='Kelsier',
        discord_id='395341154071347220',
        ancestry=1,
        is_active=True,
        stance=STANCE_NORMAL,
        hp=100,
        max_hp=100,
        armor=0,
        mobility=25,
        dexterity=25,
        endurance=100,
        max_endurance=100,
        strength=10,
        luck=5,
        experience=0,
        magic_number=0,
        fighting_skill=0,
        hunting_skill=0,
        mining_skill=0,
        cooking_skill=0,
        crafting_skill=0
    )

    session.add(new_player)

    session.commit()
