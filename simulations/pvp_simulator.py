import random

from mmobot.db.models import (
    Attire,
    ItemInstance,
    Player,
    PlayerSkill,
    PlayerStats,
    Weapon,
    WeaponInstance
)
from mmobot.utils.battle import calculate_hit_chance, calculate_hit_damage


NEW_STATS_1 = PlayerStats(
    hp=100,
    max_hp=100,
    armor=1,
    mobility=25,
    dexterity=25,
    endurance=100,
    max_endurance=100,
    strength=15,
    luck=1
)

INTERMEDIATE_STATS_1 = PlayerStats(
    hp=100,
    max_hp=100,
    armor=1,
    mobility=30,
    dexterity=60,
    endurance=120,
    max_endurance=120,
    strength=40,
    luck=1
)

ADVANCED_STATS_1 = PlayerStats(
    hp=100,
    max_hp=100,
    armor=1,
    mobility=30,
    dexterity=100,
    endurance=120,
    max_endurance=120,
    strength=40,
    luck=1
)

IRON_SWORD = WeaponInstance(
    id=25,
    item=Weapon(
        id='iron-sword',
        weapon_type='sword',
        size=50,
        weight=70,
        lethality=40
    )
)

WOODEN_SPEAR = WeaponInstance(
    id=25,
    item=Weapon(
        id='wooden-spear',
        weapon_type='spear',
        size=70,
        weight=50,
        lethality=25
    )
)

BASIC_TUNIC = ItemInstance(
    id=26,
    item=Attire(
        id='basic-tunic',
        size=6,
        weight=2,
        coverage=50,
        armor=2,
        warmth=5
    )
)


NEW_PLAYER_1 = Player(
    name='P1',
    stats=NEW_STATS_1,
    skills=[
        PlayerSkill(
            skill_name='fighting',
            skill_level=0
        ),
        PlayerSkill(
            skill_name='sword_mastery',
            skill_level=0
        )
    ],
    inventory=[
        IRON_SWORD,
        BASIC_TUNIC
    ],
    equipped_weapon_id=25,
    equipped_attire_id=26
)

INTERMEDIATE_PLAYER_1 = Player(
    name='P1',
    stats=INTERMEDIATE_STATS_1,
    skills=[
        PlayerSkill(
            skill_name='fighting',
            skill_level=30
        ),
        PlayerSkill(
            skill_name='sword-mastery',
            skill_level=20
        ),
        PlayerSkill(
            skill_name='evasion',
            skill_level=30
        )
    ],
    inventory=[
        IRON_SWORD,
        BASIC_TUNIC
    ],
    equipped_weapon_id=25,
    equipped_attire_id=26
)

ADVANCED_PLAYER_1 = Player(
    name='P1',
    stats=ADVANCED_STATS_1,
    skills=[
        PlayerSkill(
            skill_name='fighting',
            skill_level=50
        ),
        PlayerSkill(
            skill_name='sword-mastery',
            skill_level=30
        ),
        PlayerSkill(
            skill_name='evasion',
            skill_level=30
        )
    ],
    inventory=[
        IRON_SWORD,
        BASIC_TUNIC
    ],
    equipped_weapon_id=25,
    equipped_attire_id=26
)

ADVANCED_PLAYER_2 = Player(
    name='AdvancedPlayerSpear',
    stats=ADVANCED_STATS_1,
    skills=[
        PlayerSkill(
            skill_name='fighting',
            skill_level=50
        ),
        PlayerSkill(
            skill_name='spear-mastery',
            skill_level=30
        ),
        PlayerSkill(
            skill_name='evasion',
            skill_level=30
        )
    ],
    inventory=[
        WOODEN_SPEAR,
        BASIC_TUNIC
    ],
    equipped_weapon_id=25,
    equipped_attire_id=26
)

NEW_PLAYER_2 = Player(
    name='P1Spear',
    stats=NEW_STATS_1,
    skills=[],
    inventory=[
        WOODEN_SPEAR,
        BASIC_TUNIC
    ],
    equipped_weapon_id=25,
    equipped_attire_id=26
)

NEW_FIST_FIGHTER_1 = Player(
    name='P1',
    stats=NEW_STATS_1,
    skills=[
        PlayerSkill(
            skill_name='fighting',
            skill_level=0
        ),
        PlayerSkill(
            skill_name='weaponless-combat',
            skill_level=0
        )
    ],
    inventory=[
        BASIC_TUNIC
    ],
    equipped_weapon_id=None,
    equipped_attire_id=26
)

ADVANCED_FIST_FIGHTER_1 = Player(
    name='P1',
    stats=ADVANCED_STATS_1,
    skills=[
        PlayerSkill(
            skill_name='fighting',
            skill_level=50
        ),
        PlayerSkill(
            skill_name='weaponless-combat',
            skill_level=30
        ),
        PlayerSkill(
            skill_name='evasion',
            skill_level=30
        )
    ],
    inventory=[
        BASIC_TUNIC
    ],
    equipped_weapon_id=None,
    equipped_attire_id=26
)

ADVANCED_WEAVER_1 = Player(
    name='P1',
    stats=ADVANCED_STATS_1,
    skills=[
        PlayerSkill(
            skill_name='weaving',
            skill_level=50
        ),
    ],
    inventory=[
        BASIC_TUNIC
    ],
    equipped_weapon_id=None,
    equipped_attire_id=26
)


def simulate_attack(attacker, defender):
    hit_chance = calculate_hit_chance(attacker, defender)
    print('P1 attacks P2')
    print(f'Hit chance: {hit_chance}%')
    random_number = random.randint(0, 99)
    print(f'Roll: {random_number}')
    if random_number < hit_chance:
        hit_damage, hit_armor = calculate_hit_damage(attacker, defender)
        if hit_armor:
            print('P1 landed an armor hit on P2!')
        else:
            print('P1 landed a hit on P2!')
        print(f'P2 took {hit_damage} damage')
        defender.stats.hp -= hit_damage
        remaining_hp = defender.stats.hp
        if remaining_hp <= 0:
            print('P2 is incapacitated')
        elif remaining_hp <= 50:
            print('P2 is weak')
        else:
            print(f'P2 has {remaining_hp} HP remaining')
    else:
        print('P2 evaded the attack!')


simulate_attack(NEW_PLAYER_2, INTERMEDIATE_PLAYER_1)
simulate_attack(INTERMEDIATE_PLAYER_1, NEW_PLAYER_2)
simulate_attack(NEW_PLAYER_2, INTERMEDIATE_PLAYER_1)
simulate_attack(INTERMEDIATE_PLAYER_1, NEW_PLAYER_2)
simulate_attack(NEW_PLAYER_2, INTERMEDIATE_PLAYER_1)
simulate_attack(INTERMEDIATE_PLAYER_1, NEW_PLAYER_2)
simulate_attack(NEW_PLAYER_2, INTERMEDIATE_PLAYER_1)
simulate_attack(INTERMEDIATE_PLAYER_1, NEW_PLAYER_2)
