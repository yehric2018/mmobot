import random

from mmobot.db.models import PlayerStats

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
    hp = random.randint(MIN_INITIAL_HP_CAP, MAX_INITIAL_HP_CAP)
    armor = random.randint(MIN_INITIAL_ARMOR - 4, MAX_INITIAL_ARMOR)
    if armor < 0:
        armor = 0
    mobility = random.randint(MIN_INITIAL_MOBILITY, MAX_INITIAL_MOBILITY)
    endurance = random.randint(MIN_INITIAL_ENDURANCE, MAX_INITIAL_ENDURANCE)
    strength = random.randint(MIN_INITIAL_STRENGTH, MAX_INITIAL_STRENGTH)
    luck = random.randint(MIN_LUCK, MAX_LUCK)

    return PlayerStats(
        hp=hp,
        max_hp=hp,
        armor=armor,
        mobility=mobility,
        endurance=endurance,
        max_endurance=endurance,
        strength=strength,
        luck=luck,
        magic_number=0
    )


# TODO: Write tests for each of these
def find_item_with_id(inventory, numeric_id):
    for item_instance in inventory:
        if item_instance.id == numeric_id:
            return item_instance


def find_item_with_name(inventory, name):
    for item_instance in inventory:
        if item_instance.item.id == name:
            return item_instance
