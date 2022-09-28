import random


def calculate_hit_chance(attacker, defender):
    offense_score = (4/3) * (
        0.30 * attacker.dexterity +
        0.65 * attacker.fighting_skill +
        0.05 * (attacker.mobility - 25)
    ) + attacker.luck
    defense_score = (4/3) * (
        0.65 * defender.dexterity +
        0.15 * defender.fighting_skill +
        0.20 * (defender.mobility - 25)
    ) + defender.luck

    raw_percentage = int(offense_score - defense_score + 40)
    if raw_percentage < 0:
        return 0
    elif raw_percentage > 100:
        return 100
    return raw_percentage


def calculate_hit_damage(p1, p2, weapons, armors):
    p1_weapon = weapons[p1.equipped_weapon]
    p2_armor = armors[p2.equipped_armor]
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
