import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import yaml

from mmobot.constants import DB_ENTRY_SEPERATOR
from mmobot.db.models import (
    Attire,
    Base,
    FluidFood,
    Poison,
    Resource,
    SolidFood,
    Weapon,
    Zone,
    ZonePath
)

load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')
STATIC_PATH = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'static')
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
    setup_nonsolids()


def setup_zones():
    all_zones = []
    all_zone_paths = []
    with open(os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'static', 'zones.db'), 'r') as f:
        file_text = f.read()
        zone_data = file_text.split(DB_ENTRY_SEPERATOR)
        for data in zone_data:
            lines = data.split('\n')
            zone_name = lines[0]
            all_zones.append(Zone(channel_name=zone_name))
            for i in range(1, len(lines)):
                minizone_name = lines[i][1:]
                all_zones.append(Zone(channel_name=minizone_name, minizone_parent=zone_name))

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
    setup_resources()
    setup_attire()
    setup_weapons()
    setup_solid_food()

def resource_from_yml(resource_yml):
    return Resource(
        id=resource_yml['id'],
        size=resource_yml['size'],
        weight=resource_yml['weight']
    )

def setup_resources():
    resources_path = os.path.join(STATIC_PATH, 'items', 'resources')
    all_resources = []
    for resource_filename in os.listdir(resources_path):
        with open(os.path.join(resources_path, resource_filename), 'r') as f:
            try:
                resource_yml = yaml.safe_load(f)
                resource = resource_from_yml(resource_yml)
                all_resources.append(resource)
            except yaml.YAMLError as exc:
                print(exc)
    
    with Session(engine) as session:
        for resource in all_resources:
            session.merge(resource)
        session.commit()

def setup_attire():
    attire_path = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'static', 'attire.db')
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
                size=float(item_stats[0]),
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


def weapon_from_yml(weapon_yml):
    return Weapon(
        id=weapon_yml['id'],
        item_type='weapon',
        size=weapon_yml['size'],
        weight=weapon_yml['weight'],
        weapon_type=weapon_yml['weapon_type'],
        lethality=weapon_yml['lethality']
    )


def setup_weapons():
    weapons_path = os.path.join(STATIC_PATH, 'items', 'weapons')
    all_weapons = []
    for weapon_filename in os.listdir(weapons_path):
        with open(os.path.join(weapons_path, weapon_filename), 'r') as f:
            try:
                weapon_yml = yaml.safe_load(f)
                weapon = weapon_from_yml(weapon_yml)
                all_weapons.append(weapon)
            except yaml.YAMLError as exc:
                print(exc)
    
    with Session(engine) as session:
        for weapon in all_weapons:
            session.merge(weapon)
        session.commit()


def solid_food_from_yml(food_yml):
    return SolidFood(
        id=food_yml['id'],
        size=food_yml['size'],
        weight=food_yml['weight'],
        hp_recover=food_yml['hp_recover'],
        endurance_recover=food_yml['endurance_recover'],
        impairment=food_yml['impairment'],
        impairment_duration=food_yml['impairment_duration'],
        hp_relief=food_yml['hp_relief'],
        relief_duration=food_yml['relief_duration'],
        endurance_boost=food_yml['endurance_boost'],
        boost_duration=food_yml['boost_duration']
    )


def setup_solid_food():
    food_path = os.path.join(STATIC_PATH, 'items', 'solid_foods')
    all_food = []
    for food_filename in os.listdir(food_path):
        with open(os.path.join(food_path, food_filename), 'r') as f:
            try:
                food_yml = yaml.safe_load(f)
                solid_food = solid_food_from_yml(food_yml)
                all_food.append(solid_food)
            except yaml.YAMLError as exc:
                print(exc)
    
    with Session(engine) as session:
        for food in all_food:
            session.merge(food)
        session.commit()


def setup_nonsolids():
    setup_fluid_food()
    setup_poisons()

def fluid_food_from_yml(food_yml):
    return FluidFood(
        id=food_yml['id'],
        size=food_yml['size'],
        weight=food_yml['weight'],
        hp_recover=food_yml['hp_recover'],
        endurance_recover=food_yml['endurance_recover'],
        impairment=food_yml['impairment'],
        impairment_duration=food_yml['impairment_duration'],
        hp_relief=food_yml['hp_relief'],
        relief_duration=food_yml['relief_duration'],
        endurance_boost=food_yml['endurance_boost'],
        boost_duration=food_yml['boost_duration']
    )

def setup_fluid_food():
    food_path = os.path.join(STATIC_PATH, 'nonsolids', 'fluid_foods')
    all_food = []
    for food_filename in os.listdir(food_path):
        with open(os.path.join(food_path, food_filename), 'r') as f:
            try:
                food_yml = yaml.safe_load(f)
                fluid_food = fluid_food_from_yml(food_yml)
                all_food.append(fluid_food)
            except yaml.YAMLError as exc:
                print(exc)

    with Session(engine) as session:
        for food in all_food:
            session.merge(food)
        session.commit()

def poison_from_yml(poison_yml):
    return Poison(
        id=poison_yml['id'],
        size=poison_yml['size'],
        weight=poison_yml['weight'],
        damage=poison_yml['damage'],
        duration=poison_yml['duration']
    )

def setup_poisons():
    poison_path = os.path.join(STATIC_PATH, 'nonsolids', 'poisons')
    all_poisons = []
    for poison_filename in os.listdir(poison_path):
        with open(os.path.join(poison_path, poison_filename), 'r') as f:
            try:
                poison_yml = yaml.safe_load(f)
                poison = poison_from_yml(poison_yml)
                all_poisons.append(poison)
            except yaml.YAMLError as exc:
                print(exc)

    with Session(engine) as session:
        for poison in all_poisons:
            session.merge(poison)
        session.commit()


Base.metadata.create_all(engine)
setup()
