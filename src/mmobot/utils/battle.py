import random

from mmobot.constants import ATTACK_ENDURANCE_COST, BASE_HIT_CHANCE
from mmobot.db.models import Player


MAX_HIT_CHANCE = 100
MIN_HIT_CHANCE = 0


async def attack_in_channel(channel, attacker, defender):
    assert attacker.endurance > ATTACK_ENDURANCE_COST + attacker.get_burden()
    attacker_name = attacker.get_name()
    defender_name = defender.get_name()
    message = f'{attacker_name} is attacking {defender_name}\n'
    hit_chance = calculate_hit_chance(attacker, defender)
    if random.randint(0, 99) < hit_chance:
        damage = calculate_hit_damage(attacker, defender)
        defender.hp = max(defender.hp - damage, 0)
        message = f'{attacker_name} landed a hit on **{defender_name}**,'
        message += ' dealing {damage} damage.\n'
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
    if percentage < MIN_HIT_CHANCE:
        percentage = MIN_HIT_CHANCE
    if percentage > MAX_HIT_CHANCE:
        percentage = MAX_HIT_CHANCE
    return percentage


def calculate_hit_damage(attacker, defender):
    damage = attacker.get_attack_damage()
    armor = defender.get_armor()
    return max(damage - armor, 0)
