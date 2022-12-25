from mmobot.db.models import ToolInstance
from mmobot.utils.players import find_item_with_id
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id


def separate_crafting_components(references, player):
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
    for tool in player.zone.loot:
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
