import random

from mmobot.db.models import Item
from mmobot.db.models.item_instance import ItemInstance
from mmobot.utils.entities import convert_int_to_alphanum
from mmobot.utils.players import find_item_with_id


async def attack_command_mining(context, player, minable, session):
    minable_id = convert_int_to_alphanum(minable.id)
    await context.send(f'Mining [ /{minable_id} ]...')
    equipped_weapon = find_item_with_id(player.inventory, player.equipped_weapon_id)
    resources = get_mining_outcome(player.stats, equipped_weapon, minable)
    if len(resources) == 0:
        await context.send('No resources mined!')
    else:
        message = 'Mined the following resource(s):\n'
        item_instances = []
        for resource in resources:
            item_instances.append(ItemInstance(player_id=player.id, item_id=resource.id))
            message += f'    - {resource.id}\n'
        session.add_all(item_instances)
        await context.send(message)

    if player.equipped_weapon_id is None:
        await context.send('You lost 2 HP while mining with bare hands.')


MAX_MINING_STRENGTH = 100
STRENGTH_PER_RESOURCE = 20

MINING_RESOURCE_STONE = Item(
    id='stone',
    size=5,
    weight=5
)

MINING_RESOURCE_COAL = Item(
    id='coal',
    size=5,
    weight=5
)

MINING_RESOURCE_IRON = Item(
    id='iron-ore',
    size=5,
    weight=5
)

MINING_RESOURCE_COPPER = Item(
    id='copper-ore',
    size=5,
    weight=5
)

MINING_RESOURCE_SILVER = Item(
    id='silver-ore',
    size=5,
    weight=5
)

MINING_RESOURCE_GOLD = Item(
    id='golden-ore',
    size=5,
    weight=5
)

MINING_RESOURCE_DIAMOND = Item(
    id='diamond-ore',
    size=5,
    weight=5
)

MINING_RESOURCE_PLATINUM = Item(
    id='platinum-ore',
    size=5,
    weight=5
)

STANDARD_MINING_COMPOSITION = [
    MINING_RESOURCE_STONE,
    MINING_RESOURCE_COAL,
    MINING_RESOURCE_IRON,
    MINING_RESOURCE_SILVER,
    MINING_RESOURCE_GOLD,
    MINING_RESOURCE_DIAMOND,
    MINING_RESOURCE_PLATINUM
]


def get_mining_outcome(player_stats, weapon_instance, minable):
    endurance_ratio = player_stats.endurance / player_stats.max_endurance
    mining_score = int(player_stats.strength * endurance_ratio)
    if weapon_instance is None:
        player_stats.hp -= 2
        player_stats.endurance -= 4
    else:
        weapon = weapon_instance.item
        if weapon.weapon_type == 'pickaxe':
            mining_score += weapon.lethality
            player_stats.endurance -= 1
        else:
            mining_score += weapon.lethality // 4
            player_stats.endurance -= 2
    mining_score += player_stats.luck
    num_resources = random.randint(0, mining_score) // STRENGTH_PER_RESOURCE

    resources = []
    for _ in range(num_resources):
        resource_distribution = get_mining_resource_distribution(minable)
        total_composition = resource_distribution[-1]
        mining_number = random.randint(1, total_composition)
        for i in range(len(resource_distribution)):
            if mining_number <= resource_distribution[i]:
                resources.append(STANDARD_MINING_COMPOSITION[i])
                update_minable(minable, i)
                break
    return resources


def get_mining_resource_distribution(minable):
    distribution = []
    distribution.append(minable.stone_comp)
    distribution.append(distribution[-1] + minable.coal_comp)
    distribution.append(distribution[-1] + minable.iron_comp)
    distribution.append(distribution[-1] + minable.silver_comp)
    distribution.append(distribution[-1] + minable.gold_comp)
    distribution.append(distribution[-1] + minable.diamond_comp)
    distribution.append(distribution[-1] + minable.platinum_comp)
    return distribution


def update_minable(minable, resource_index):
    match STANDARD_MINING_COMPOSITION[resource_index].id:
        case 'stone':
            minable.stone_comp -= 1
        case 'coal':
            minable.coal_comp -= 1
        case 'iron-ore':
            minable.iron_comp -= 1
        case 'silver-ore':
            minable.silver_comp -= 1
        case 'golden-ore':
            minable.gold_comp -= 1
        case 'diamond-ore':
            minable.diamond_comp -= 1
        case 'platinum-ore':
            minable.platinum_comp -= 1
