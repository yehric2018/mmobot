import random

NEW_PLAYER_1 = {
    'hp': 100,
    'max_hp': 100,
    'armor': 1,
    'mobility': 25,
    'dexterity': 25,
    'endurance': 100,
    'max_endurance': 100,
    'strength': 15,
    'luck': 1,
    'sword_skill': 0,
    'armor_coverage': 30,
    'armor_defense': 5,
    'sword_damage': 40
}

ADVANCED_SWORD_PLAYER = {
    'hp': 100,
    'max_hp': 100,
    'armor': 1,
    'mobility': 30,
    'dexterity': 60,
    'endurance': 120,
    'max_endurance': 120,
    'strength': 40,
    'luck': 1,
    'sword_skill': 65,
    'armor_coverage': 60,
    'armor_defense': 35,
    'sword_damage': 100
}

MAX_SWORD_PLAYER = {
    'hp': 150,
    'max_hp': 150,
    'armor': 15,
    'mobility': 100,
    'dexterity': 75,
    'endurance': 150,
    'max_endurance': 150,
    'strength': 75,
    'luck': 1,
    'sword_skill': 75,
    'armor_coverage': 100,
    'armor_defense': 100,
    'sword_damge': 900
}

attacker = ADVANCED_SWORD_PLAYER
defender = NEW_PLAYER_1

def calculate_hit_chance(p1, p2):
    offense_score = (4/3) * (0.30 * p1['dexterity'] + 0.65 * p1['sword_skill'] + 0.05 * (p1['mobility'] - 25)) + p1['luck']
    defense_score = (4/3) * (0.65 * p2['dexterity'] + 0.15 * p2['sword_skill'] + 0.20 * (p2['mobility'] - 25)) + p2['luck']

    raw_percentage = int(offense_score - defense_score + 40)
    if raw_percentage < 0:
        return 0
    elif raw_percentage > 100:
        return 100
    return raw_percentage

def calculate_hit_damage(p1, p2):
    random_number = random.randint(0, 99)
    total_defense = p2['armor']
    if random_number < p2['armor_coverage']:
        total_defense += p2['armor_defense']
    else:
        random_number = random.randint(1, 5)
        if random_number == 1:
            return 999
    skill_ratio = p1['sword_skill'] / 75 / 2
    total_attack = p1['strength'] + p1['sword_damage'] * (0.5 + skill_ratio)
    final_damage = total_attack - total_defense
    if p2['luck'] > p1['luck']:
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
    hit_damage = calculate_hit_damage(attacker, defender)
    print(f'P2 took {hit_damage} damage')
    remaining_hp = defender['hp'] - hit_damage
    if remaining_hp <= 0:
        print(f'P2 is incapacitated')
    elif remaining_hp <= 50:
        print('P2 is weak')
    else:
        print(f'P2 has {remaining_hp} HP remaining')
else:
    print('P2 evaded the attack!')