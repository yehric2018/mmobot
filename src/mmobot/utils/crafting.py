from mmobot.db.models import (
    FluidContainer,
    FluidContainerInstance,
    ItemInstance,
    Nonsolid,
    SolidFood,
    SolidFoodInstance,
    Tool,
    ToolInstance,
    Weapon,
    WeaponInstance
)
from mmobot.utils.players import find_item_with_id
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id


def separate_crafting_components(references, player, zone):
    entity_ids = set()
    for reference in references:
        if not is_entity_id(reference):
            return {'error': reference}
        entity_ids.add(convert_alphanum_to_int(reference))
    if player.equipped_weapon_id is not None:
        handheld = find_item_with_id(player.inventory, player.equipped_weapon_id)
    else:
        handheld = None
    tools = []
    for tool in zone.loot:
        if tool.id in entity_ids and isinstance(tool, ToolInstance):
            tools.append(tool)
            entity_ids.remove(tool.id)
    ingredients = []
    for ingredient in player.inventory:
        if ingredient.id in entity_ids and ingredient != handheld:
            ingredients.append(ingredient)
            entity_ids.remove(ingredient.id)
    return {
        'ingredients': ingredients,
        'tools': tools,
        'handheld': handheld,
        'skills': player.skills
    }


def find_best_recipe(goal_item, recipes, player, ingredients, tools, handheld):
    best_recipe = None
    best_endurance_cost = 999999
    missing_ingredients = None
    missing_container = False
    insufficient_skill = False

    for recipe in recipes:
        current_missing = recipe.get_missing_ingredients(ingredients)
        if len(current_missing) != 0:
            missing_ingredients = current_missing
            continue
        if (isinstance(goal_item, Nonsolid)
                and recipe.is_missing_container(ingredients)):
            missing_container = True
            continue
        crafting_skill = recipe.get_crafting_skill(player.skills)
        if crafting_skill == -1:
            insufficient_skill = True
            continue
        endurance_cost = recipe.get_endurance_cost(
            player,
            tools=tools,
            handheld=handheld,
            crafting_skill=crafting_skill
        )
        if endurance_cost < best_endurance_cost:
            best_recipe = recipe
            best_endurance_cost = endurance_cost

    if best_recipe is None:
        if missing_ingredients:
            return {'error': 'Missing ingredients for recipe(s).'}
        elif missing_container:
            return {'error': 'Missing empty container to store final contents.'}
        elif insufficient_skill:
            return {'error': 'Insufficient skill to craft'}
        return {'error': 'Unknown error, please try again'}

    return {
        'recipe': best_recipe,
        'cost': best_endurance_cost
    }


def create_item_instance(item, condition=99999):
    if isinstance(item, Weapon):
        return WeaponInstance(item_id=item.id)
    elif isinstance(item, Tool):
        return ToolInstance(item_id=item.id)
    elif isinstance(item, SolidFood):
        return SolidFoodInstance(item_id=item.id)
    elif isinstance(item, FluidContainer):
        return FluidContainerInstance(item_id=item.id, units=0)
    return ItemInstance(item_id=item.id)
