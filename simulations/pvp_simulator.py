from mmobot.db.index import MonsterIndex
from mmobot.db.models import (
    MonsterInstance,
    Player,
    PlayerSkill,
    Weapon,
    WeaponInstance
)
from mmobot.utils.battle import calculate_hit_chance, calculate_hit_damage


def skill(name, level):
    return PlayerSkill(skill_name=name, skill_level=level)


monster_index = MonsterIndex().index


IRON_SWORD = Weapon(id='iron-sword', weapon_type='sword', lethality=40, range=13)
IRONHEAD_SPEAR = Weapon(id='ironhead-spear', weapon_type='spear', lethality=45, range=20)
IRON_AXE = Weapon(id='iron-axe', weapon_type='axe', lethality=55, range=8)


NEW_PLAYER_SWORD = Player(
    name='NewSwordsman',
    hp=100, endurance=100,
    max_hp=100, max_endurance=100, strength=100, mobility=100,
    skills=[],
    equipped_weapon=WeaponInstance(item=IRON_SWORD)
)

NEW_PLAYER_FIST = Player(
    name='NewFistFighter',
    hp=100, endurance=100,
    max_hp=100, max_endurance=100, strength=100, mobility=100,
    skills=[],
    equipped_weapon=None
)

NEW_PLAYER_SPEAR = Player(
    name='NewSpearFighter',
    hp=100, endurance=100,
    max_hp=100, max_endurance=100, strength=100, mobility=100,
    skills=[],
    equipped_weapon=WeaponInstance(item=IRONHEAD_SPEAR)
)

NEW_PLAYER_AXE = Player(
    name='NewAxeFighter',
    hp=100, endurance=100,
    max_hp=100, max_endurance=100, strength=100, mobility=100,
    skills=[],
    equipped_weapon=WeaponInstance(item=IRON_AXE)
)

INTERMEDIATE_SWORD_FIGHTER = Player(
    name='IntermediateSwordFighter',
    hp=100, endurance=100,
    max_hp=100, max_endurance=100, strength=100, mobility=100,
    skills=[skill('fighting', 20), skill('sword-mastery', 10), skill('evasion', 0)],
    equipped_weapon=WeaponInstance(item=IRON_SWORD)
)

ADVANCED_SWORD_FIGHTER = Player(
    name='ExpertSwordsman',
    hp=100, endurance=200,
    max_hp=100, max_endurance=200, strength=180, mobility=100,
    skills=[skill('fighting', 50), skill('sword-mastery', 50), skill('evasion', 50)],
    equipped_weapon=WeaponInstance(item=IRON_SWORD)
)

ADVANCED_SWORD_WOUNDED = Player(
    name='WoundedExpertSwordsman',
    hp=50, endurance=200,
    max_hp=100, max_endurance=200, strength=180, mobility=100,
    skills=[skill('fighting', 50), skill('sword-mastery', 50), skill('evasion', 50)],
    equipped_weapon=WeaponInstance(item=IRON_SWORD)
)

ALMOST_MAXED_SWORD_FIGHTER = Player(
    name='GreatSwordsman',
    hp=100, endurance=200,
    max_hp=100, max_endurance=200, strength=180, mobility=100,
    skills=[skill('fighting', 40), skill('sword-mastery', 40), skill('evasion', 50)],
    equipped_weapon=WeaponInstance(item=IRON_SWORD)
)


ADVANCED_SPEAR_FIGHTER = Player(
    name='ExpertSpearman',
    hp=100, endurance=200,
    max_hp=100, max_endurance=200, strength=180, mobility=100,
    skills=[skill('fighting', 50), skill('spear-mastery', 50), skill('evasion', 50)],
    equipped_weapon=WeaponInstance(item=IRONHEAD_SPEAR)
)

ADVANCED_SPEAR_TANK = Player(
    name='ExpertPaladin',
    hp=100, endurance=200,
    max_hp=200, max_endurance=140, strength=140, mobility=100,
    skills=[skill('fighting', 50), skill('spear-mastery', 50), skill('evasion', 50)],
    equipped_weapon=WeaponInstance(item=IRONHEAD_SPEAR)
)

ADVANCED_HUNTER = Player(
    name='ExpertHunter',
    hp=100, endurance=180,
    max_hp=100, max_endurance=180, strength=180, mobility=200,
    skills=[skill('evasion', 50)]
)

ADVANCED_MONK = Player(
    name='ExpertMonk',
    hp=150, endurance=200,
    max_hp=150, max_endurance=200, strength=130, mobility=200,
    skills=[skill('evasion', 50)]
)

GOBLIN_MONSTER = MonsterInstance.create_instance(monster_index['goblin'])
GOBLIN_MONSTER.id = 600

DRAGON_MONSTER = MonsterInstance.create_instance(monster_index['dragon'])
DRAGON_MONSTER.id = 601

BEAR_MONSTER = MonsterInstance.create_instance(monster_index['bear'])
BEAR_MONSTER.id = 602


def simulate_attack(attacker, defender):
    hit_chance = calculate_hit_chance(attacker, defender)
    print(f'{attacker.get_name()} attacks {defender.get_name()}')
    print(f'\tHit chance: {hit_chance}%')
    hit_damage = calculate_hit_damage(attacker, defender)
    print(f'\tIf hit: deals {hit_damage} damage')


simulate_attack(NEW_PLAYER_SWORD, NEW_PLAYER_SWORD)
simulate_attack(NEW_PLAYER_FIST, NEW_PLAYER_SWORD)
simulate_attack(NEW_PLAYER_SWORD, NEW_PLAYER_FIST)
simulate_attack(NEW_PLAYER_SWORD, NEW_PLAYER_AXE)
simulate_attack(NEW_PLAYER_SWORD, GOBLIN_MONSTER)
simulate_attack(GOBLIN_MONSTER, NEW_PLAYER_SWORD)

simulate_attack(NEW_PLAYER_SWORD, ADVANCED_SWORD_FIGHTER)
simulate_attack(ADVANCED_SWORD_FIGHTER, NEW_PLAYER_SWORD)
simulate_attack(NEW_PLAYER_SWORD, ADVANCED_HUNTER)
simulate_attack(ADVANCED_SWORD_FIGHTER, GOBLIN_MONSTER)
simulate_attack(GOBLIN_MONSTER, ADVANCED_SWORD_FIGHTER)

simulate_attack(NEW_PLAYER_SWORD, BEAR_MONSTER)
simulate_attack(BEAR_MONSTER, NEW_PLAYER_SWORD)
simulate_attack(ADVANCED_SWORD_FIGHTER, BEAR_MONSTER)
simulate_attack(BEAR_MONSTER, ADVANCED_SWORD_FIGHTER)

simulate_attack(ADVANCED_SWORD_FIGHTER, ADVANCED_HUNTER)
simulate_attack(ADVANCED_SWORD_FIGHTER, ADVANCED_SWORD_FIGHTER)
simulate_attack(ADVANCED_SWORD_FIGHTER, ADVANCED_SWORD_WOUNDED)
simulate_attack(ADVANCED_SWORD_WOUNDED, ADVANCED_SWORD_FIGHTER)
simulate_attack(ADVANCED_SWORD_FIGHTER, ALMOST_MAXED_SWORD_FIGHTER)
simulate_attack(ALMOST_MAXED_SWORD_FIGHTER, ADVANCED_SWORD_FIGHTER)
simulate_attack(ADVANCED_SWORD_FIGHTER, ADVANCED_SPEAR_FIGHTER)
simulate_attack(ADVANCED_SPEAR_FIGHTER, ADVANCED_SWORD_FIGHTER)
simulate_attack(ADVANCED_SWORD_FIGHTER, ADVANCED_SPEAR_TANK)
simulate_attack(ADVANCED_SPEAR_TANK, ADVANCED_SWORD_FIGHTER)

simulate_attack(ADVANCED_SWORD_FIGHTER, DRAGON_MONSTER)
simulate_attack(DRAGON_MONSTER, ADVANCED_SWORD_FIGHTER)
simulate_attack(NEW_PLAYER_SWORD, DRAGON_MONSTER)
simulate_attack(DRAGON_MONSTER, NEW_PLAYER_SWORD)

print('----------INTERMEDIATE SWORD FIGHTER----------')
simulate_attack(INTERMEDIATE_SWORD_FIGHTER, NEW_PLAYER_SWORD)
simulate_attack(NEW_PLAYER_SWORD, INTERMEDIATE_SWORD_FIGHTER)
simulate_attack(INTERMEDIATE_SWORD_FIGHTER, ADVANCED_SWORD_FIGHTER)
simulate_attack(ADVANCED_SWORD_FIGHTER, INTERMEDIATE_SWORD_FIGHTER)
simulate_attack(INTERMEDIATE_SWORD_FIGHTER, DRAGON_MONSTER)
simulate_attack(DRAGON_MONSTER, INTERMEDIATE_SWORD_FIGHTER)
