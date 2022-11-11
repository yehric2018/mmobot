import random


MAX_HIT_CHANCE = 100
MIN_HIT_CHANCE = 0
ENDURANCE_THRESHOLD = 100
HP_THRESHOLD = 100


async def attack_command_pvp(context, attacker, defender):
    message = f'{attacker.name} is attacking {defender.name}\n'
    hit_chance = calculate_hit_chance(attacker, defender)
    if random.randint(0, 99) < hit_chance:
        hit_damage, hit_armor = calculate_hit_damage(attacker, defender)
        if hit_armor:
            message += f'{attacker.name} landed an armor hit on {defender.name}!\n'
        else:
            message += f'{attacker.name} landed a hit on {defender.name}, '
        message += f'dealing {hit_damage} damage\n'
        defender.stats.hp -= hit_damage
        if defender.stats.hp < 60:
            message += f'{defender.name} is wounded\n'
        elif defender.stats.hp < 30:
            message += f'{defender.name} is gravely wounded\n'
        elif defender.stats.hp == 0:
            message += f'{defender.name} is incapacitated\n'
    else:
        message += f'{defender.name} evaded the attack\n'
    await context.send(message)

    defending_member = context.message.mentions[0]
    await defending_member.send(f'You have {defender.stats.hp} HP remaining')


def calculate_hit_chance(attacker, defender):
    attacker_weapon = get_equipped_weapon(attacker)
    defender_weapon = get_equipped_weapon(defender)
    offense_score = calculate_offense_score(attacker, attacker_weapon)
    defense_score = calculate_defense_score(defender, defender_weapon)
    percentage = 50 + (offense_score - defense_score)
    if percentage < 0:
        percentage = 0
    if percentage > 100:
        percentage = 100
    return percentage


def calculate_hit_damage(attacker, defender):
    weapon = get_equipped_weapon(attacker)
    weapon_skill = get_weapon_skill(attacker, weapon)
    attire = get_equipped_attire(defender)

    attire_coverage = 0
    attire_armor = 0
    lethality = 0
    if attire is not None:
        attire_coverage = attire.item.coverage
        attire_armor = attire.item.armor
    if weapon is not None:
        skill_ratio = (70 + weapon_skill) / 100
        lethality = weapon.item.lethality * skill_ratio
    armor_hit = False

    total_damage = 0.4 * attacker.stats.strength + lethality
    total_damage -= defender.stats.armor
    if attire_coverage >= random.randint(1, 100):
        armor_hit = True
        total_damage -= attire_armor
    if total_damage < 0:
        total_damage = 0
    return (int(total_damage), armor_hit)


def calculate_offense_score(player, weapon):
    fighting_skill = get_fighting_skill(player)
    weapon_skill = get_weapon_skill(player, weapon)
    dexterity = player.stats.dexterity
    mobility = player.stats.mobility
    luck = player.stats.luck
    weapon_bonus = get_weapon_bonus(weapon)
    endurance_ratio = min(1.0, player.stats.endurance / ENDURANCE_THRESHOLD)
    hp_ratio = min(1.0, player.stats.hp / HP_THRESHOLD)

    offense_score = 0.4 * fighting_skill + 0.45 * weapon_skill
    offense_score += 0.3 * dexterity
    offense_score += 0.1 * mobility
    offense_score += weapon_bonus
    offense_score += luck / 7
    offense_score *= (endurance_ratio * hp_ratio)

    return offense_score


def calculate_defense_score(player, weapon):
    fighting_skill = get_fighting_skill(player)
    weapon_skill = get_weapon_skill(player, weapon)
    evasion_skill = get_evasion_skill(player)
    dexterity = player.stats.dexterity
    mobility = player.stats.mobility
    luck = player.stats.luck
    weapon_bonus = get_weapon_bonus(weapon)
    endurance_ratio = min(1.0, player.stats.endurance / ENDURANCE_THRESHOLD)
    hp_ratio = min(1.0, player.stats.hp / HP_THRESHOLD)

    defense_score = 0.35 * fighting_skill + 0.35 * weapon_skill
    defense_score += 0.4 * evasion_skill
    defense_score += 0.2 * dexterity
    defense_score += 0.3 * mobility
    defense_score += weapon_bonus
    defense_score += luck / 7
    defense_score *= (endurance_ratio * hp_ratio)

    return defense_score


def get_fighting_skill(player):
    for skill in player.skills:
        if skill.skill_name == 'fighting':
            return skill.skill_level
    return 0


def get_weapon_skill(player, weapon):
    if weapon is None:
        skill_name = 'weaponless-combat'
    else:
        match weapon.item.weapon_type:
            case 'sword':
                skill_name = 'sword-mastery'
            case 'knife':
                skill_name = 'knife-mastery'
            case 'spear':
                skill_name = 'spear-mastery'
            case 'axe':
                skill_name = 'axe-mastery'
            case _:
                return 0
    for skill in player.skills:
        if skill.skill_name == skill_name:
            return skill.skill_level
    return 0


def get_evasion_skill(player):
    for skill in player.skills:
        if skill.skill_name == 'evasion':
            return skill.skill_level
    return 0


def get_equipped_weapon(player):
    return find_item_in_inventory(player.equipped_weapon_id, player.inventory)


def get_equipped_attire(player):
    return find_item_in_inventory(player.equipped_attire_id, player.inventory)


def find_item_in_inventory(item_id, inventory):
    if item_id is not None:
        for item in inventory:
            if item.id == item_id:
                return item
    return None


def get_weapon_bonus(weapon):
    if weapon is None:
        return 0

    match weapon.item.weapon_type:
        case 'sword':
            return 20
        case 'spear':
            return 30
        case 'axe':
            return 15
        case 'knife':
            return 5
    return 0
