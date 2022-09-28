import random

from mmobot.db.models import Player
from mmobot.constants import STANCE_NORMAL
from mmobot.utils.battle import calculate_hit_chance, calculate_hit_damage


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
    equipped_attire='leather armor'
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
    equipped_attire='silver mail'
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
    equipped_attire='silver mail'
)

FIST_FIGHTER_1 = Player(
    stance=STANCE_NORMAL,
    hp=100,
    max_hp=100,
    armor=1,
    mobility=25,
    dexterity=10,
    endurance=100,
    max_endurance=100,
    strength=10,
    luck=1,
)


attacker = ADVANCED_PLAYER_1
attacker_weapon = SILVER_SWORD
attacker_armor = SILVER_MAIL
defender = NEW_PLAYER_1
defender_weapon = IRON_SWORD
defender_armor = LEATHER_ARMOR

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
