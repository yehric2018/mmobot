from datetime import timedelta

# Combat

BASE_HIT_CHANCE = 30
WEAPONLESS_LETHALITY = 5


# Stats

HEALTHY_PLAYER_THRESHOLD = 30  # hp > 30 means player is generally healthy

ATTACK_ENDURANCE_COST = 2
MOVE_ENDURANCE_COST = 4

# Skills

ALL_SKILLS = {
    'fighting': {
        'max': 50
    },
    'marksmanship': {
        'max': 50
    },
    'smithing': {
        'max': 50
    },
    'farming': {
        'max': 50
    },
    'cooking': {
        'max': 50
    },
    'fishing': {
        'max': 50
    },
    'weaving': {
        'max': 50
    },
    'carpentry': {
        'max': 50
    },
    'masonry': {
        'max': 50
    },
    'medicine': {
        'max': 50
    }
}
LEARNING_COOLDOWN = timedelta(hours=20)
TEACHING_COOLDOWN = timedelta(hours=8)
TEACHING_DIFF = 5

# Stances
STANCE_NORMAL = 0
STANCE_BATTLE = 1
STANCE_GUARD = 2
STANCE_REST = 3
STANCE_SLEEP = 4

DB_ENTRY_SEPERATOR = '\n====================\n'

# Discord permissions
PERMISSIONS_DEFAULT = 0

# Movement
DIRECTION_NORTH = 1
DIRECTION_EAST = 2
DIRECTION_SOUTH = 3
DIRECTION_WEST = 4

BASE_MOVEMENT_COOLDOWN = timedelta(minutes=2)
