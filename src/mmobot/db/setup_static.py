from ctypes import sizeof
import os
from turtle import window_height
from unicodedata import name

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, Item, Weapon

load_dotenv()
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_DATABASE_NAME = os.getenv('MYSQL_DATABASE_NAME')

engine = create_engine(f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}/{MYSQL_DATABASE_NAME}')

DB_ENTRY_SEPERATOR = '\n====================\n'

def setup():
    setup_items()

def setup_items():
    setup_weapons()

def setup_weapons():
    with open('weapons.db', 'r') as f:
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