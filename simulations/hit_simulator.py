import random

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

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


IRON_SWORD = {
    'damage': 40,
    'weight': 100
}

SILVER_SWORD = {
    'damage': 100,
    'weight': 120
}

OP_SWORD = {
    'damage': 900,
    'weight': 0
}

LEATHER_ARMOR = {
    'armor': 5,
    'coverage': 30,
    'weight': 50
}

SILVER_MAIL = {
    'armor': 35,
    'coverage': 60,
    'weight': 150
}

OP_ARMOR = {
    'armor': 200,
    'coverage': 100,
    'weight': 0
}

NEW_PLAYER_1 = Player(
    hp=100,
    max_hp=100,
    armor=1,
    mobility=25,
    dexterity=25,
    endurance=100,
    max_endurance=100,
    strength=15,
    luck=1,
    fighting_skill=0,
    equipped_weapon='iron sword',
    equipped_armor='leather armor'
)

ADVANCED_PLAYER_1 = Player(
    hp=100,
    max_hp=100,
    armor=1,
    mobility=30,
    dexterity=60,
    endurance=120,
    max_endurance=120,
    strength=40,
    luck=1,
    fighting_skill=65,
    equipped_weapon='silver sword',
    equipped_armor='silver mail'
)

MAX_SWORD_PLAYER = Player(
    hp=150,
    max_hp=150,
    armor=15,
    mobility=100,
    dexterity=75,
    endurance=150,
    max_endurance=150,
    strength=75,
    luck=1,
    fighting_skill=75,
    equipped_weapon='silver sword',
    equipped_armor='silver mail'
)


attacker = ADVANCED_PLAYER_1
attacker_weapon = SILVER_SWORD
attacker_armor = SILVER_MAIL
defender = NEW_PLAYER_1
defender_weapon = IRON_SWORD
defender_armor = LEATHER_ARMOR


def calculate_hit_chance(p1, p2):
    offense_score = (4/3) * (
        0.30 * p1.dexterity +
        0.65 * p1.fighting_skill +
        0.05 * (p1.mobility - 25)
    ) + p1.luck
    defense_score = (4/3) * (
        0.65 * p2.dexterity +
        0.15 * p2.fighting_skill +
        0.20 * (p2.mobility - 25)
    ) + p2.luck

    raw_percentage = int(offense_score - defense_score + 40)
    if raw_percentage < 0:
        return 0
    elif raw_percentage > 100:
        return 100
    return raw_percentage


def calculate_hit_damage(p1, p1_weapon, p2, p2_armor):
    random_number = random.randint(0, 99)
    total_defense = p2.armor
    if random_number < p2_armor['coverage']:
        total_defense += p2_armor['armor']
    else:
        random_number = random.randint(1, 5)
        if random_number == 1:
            return 999
    skill_ratio = p1.fighting_skill / 75 / 2
    total_attack = p1.strength + p1_weapon['damage'] * (0.5 + skill_ratio)
    final_damage = total_attack - total_defense
    if p2.luck > p1.luck:
        final_damage -= 1
    if final_damage < 0:
        return 0
    return int(final_damage)


hit_chance = calculate_hit_chance(attacker, defender)
print('P1 attacks P2')
print(f'Hit chance: {hit_chance}%')
random_number = random.randint(0, 99)
print(f'Roll: {random_number}')
if random_number < hit_chance:
    print('P1 landed a hit on P2!')
    hit_damage = calculate_hit_damage(attacker, attacker_weapon, defender, defender_armor)
    print(f'P2 took {hit_damage} damage')
    remaining_hp = defender.hp - hit_damage
    if remaining_hp <= 0:
        print('P2 is incapacitated')
    elif remaining_hp <= 50:
        print('P2 is weak')
    else:
        print(f'P2 has {remaining_hp} HP remaining')
else:
    print('P2 evaded the attack!')
