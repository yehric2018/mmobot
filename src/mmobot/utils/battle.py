import math
import random

from mmobot.constants import ATTACK_ENDURANCE_COST, BASE_HIT_CHANCE
from mmobot.db.models import Player


MAX_HIT_CHANCE = 100
MIN_HIT_CHANCE = 0
ENDURANCE_THRESHOLD = 100
HP_THRESHOLD = 100


async def attack_command_pvp(context, attacker, defender):
    message = f'{attacker.name} is attacking {defender.name}\n'
    hit_chance = calculate_hit_chance(attacker, defender)
    if random.randint(0, 99) < hit_chance:
        damage = calculate_hit_damage(attacker, defender)
        defender.hp = max(defender.hp - damage, 0)
        message = f'{attacker.name} landed a hit on {defender.name}, '
        message += f'dealing {math.ceil(damage)} damage.\n'
        message += f'<@{defender.discord_id}> You have {math.ceil(defender.hp)} HP remaining'
    else:
        message += f'{defender.name} evaded the attack\n'
    attacker.endurance -= (ATTACK_ENDURANCE_COST + attacker.get_burden())
    await context.send(message)


async def attack_in_channel(channel, attacker, defender):
    attacker_name = attacker.get_name()
    defender_name = defender.get_name()
    message = f'{attacker_name} is attacking {defender_name}\n'
    hit_chance = calculate_hit_chance(attacker, defender)
    if random.randint(0, 99) < hit_chance:
        damage = calculate_hit_damage(attacker, defender)
        defender.hp = max(defender.hp - damage, 0)
        message = f'{attacker_name} landed a hit on {defender_name}, dealing {damage} damage.\n'
        if isinstance(defender, Player):
            message += f'<@{defender.discord_id}> You have {defender.hp} HP remaining'
    else:
        message += f'{defender_name} evaded the attack\n'
    attacker.endurance -= (ATTACK_ENDURANCE_COST + attacker.get_burden())
    await channel.send(message)


def calculate_hit_chance(attacker, defender):
    offense_score = attacker.get_offense_score()
    defense_score = defender.get_defense_score()
    percentage = BASE_HIT_CHANCE + (offense_score - defense_score)
    if percentage < 0:
        percentage = 0
    if percentage > 100:
        percentage = 100
    return percentage


def calculate_hit_damage(attacker, defender):
    damage = attacker.get_attack_damage()
    armor = defender.get_armor()
    return max(damage - armor, 0)
