import random

MIN_INITIAL_HP_CAP = 95
MAX_INITIAL_HP_CAP = 105
MIN_INITIAL_ARMOR = 0
MAX_INITIAL_ARMOR = 5
MIN_INITIAL_MOBILITY = 23
MAX_INITIAL_MOBILITY = 27
MIN_INITIAL_DEXTERITY = 23
MAX_INITIAL_DEXTERITY = 27
MIN_INITIAL_ENDURANCE = 95
MAX_INITIAL_ENDURANCE = 105
MIN_INITIAL_STRENGTH = 23
MAX_INITIAL_STRENGTH = 27

MIN_LUCK = 1
MAX_LUCK = 7


def roll_initial_stats():
    stats = {}
    stats['hp'] = random.randint(MIN_INITIAL_HP_CAP, MAX_INITIAL_HP_CAP)
    stats['armor'] = random.randint(MIN_INITIAL_ARMOR - 4, MAX_INITIAL_ARMOR)
    if stats['armor'] < 0:
        stats['armor'] = 0
    stats['mobility'] = random.randint(MIN_INITIAL_MOBILITY, MAX_INITIAL_MOBILITY)
    stats['dexterity'] = random.randint(MIN_INITIAL_DEXTERITY, MAX_INITIAL_DEXTERITY)
    stats['endurance'] = random.randint(MIN_INITIAL_ENDURANCE, MAX_INITIAL_ENDURANCE)
    stats['strength'] = random.randint(MIN_INITIAL_STRENGTH, MAX_INITIAL_STRENGTH)
    stats['luck'] = random.randint(MIN_LUCK, MAX_LUCK)
    return stats
