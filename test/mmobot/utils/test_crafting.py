import pytest

from mmobot.db.models import (
    FluidContainerInstance,
    ItemInstance,
    Player,
    PlayerSkill,
    ToolInstance,
    WeaponInstance,
    Zone
)
from mmobot.test.db import init_test_engine
from mmobot.test.mock import MockItemIndex
from mmobot.utils.crafting import find_best_recipe, separate_crafting_components


engine = init_test_engine()


item_index = MockItemIndex()

MESSAGE_MISSING_INGREDIENTS = 'Missing ingredients for recipe(s).'
MESSAGE_EMPTY_CONTAINER = 'Missing empty container to store final contents.'
MESSAGE_MISSING_SKILLS = 'Insufficient skill to craft'


@pytest.fixture
def recipes_liquid():
    return item_index.recipes['strange-liquid']


@pytest.fixture
def inventory():
    return [
        ItemInstance(id=1, item_id='stone'),
        ItemInstance(id=3, item_id='iron-ore'),
        FluidContainerInstance(id=4, item_id='stone-bowl', nonsolid_id='water', units=3),
        FluidContainerInstance(id=9, 
                item_id='stone-bowl', item=item_index.index['stone-bowl'], units=0),
        WeaponInstance(id=2, item_id='iron-hammer', item=item_index.index['iron-hammer']),
        ItemInstance(id=200, item_id='not-included'),
    ]


@pytest.fixture
def zone():
    zone_loot = [
        ItemInstance(id=201, item_id='not-included'),
        ToolInstance(id=6, item_id='iron-anvil', item=item_index.index['iron-anvil']),
        ItemInstance(id=7, item_id='not-included')
    ]
    return Zone(channel_name='town-square', loot=zone_loot)


@pytest.fixture
def skills():
    return [PlayerSkill(skill_name='skill', skill_level=15)]


def test_separateCraftingComponents_invalidReference():
    references = ['/123', '/abc', 'nope', '/xyz']
    error_message = separate_crafting_components(references, None)
    assert error_message['error'] == 'nope'


def test_separateCraftingComponents_success(inventory, zone, skills):
    references = ['/7', '/1', '/2', '/5', '/3', '/6', '/4']
    player = Player(
        id=100,
        equipped_weapon_id=2,
        inventory=inventory,
        skills=skills,
        zone=zone
    )
    components = separate_crafting_components(references, player)
    assert 'error' not in components
    assert len(components['ingredients']) == 3
    assert inventory[0] in components['ingredients']
    assert inventory[1] in components['ingredients']
    assert inventory[2] in components['ingredients']
    assert inventory[3] not in components['ingredients']
    assert inventory[4] not in components['ingredients']
    assert len(components['tools']) == 1
    assert zone.loot[0] not in components['tools']
    assert zone.loot[1] in components['tools']
    assert zone.loot[2] not in components['tools']
    assert components['handheld'] is not None
    assert components['handheld'] == inventory[4]
    assert len(components['skills']) == 1
    assert components['skills'][0] == skills[0]


def test_findBestRecipe_success(recipes_liquid, inventory, skills, zone):
    references = ['/1', '/3', '/4', '/6', '/9']
    player = Player(
        id=100,
        equipped_weapon_id=2,
        inventory=inventory,
        skills=skills,
        zone=zone
    )
    components = separate_crafting_components(references, player)
    actual = find_best_recipe(item_index.index['strange-liquid'], recipes_liquid, player,
            components['ingredients'], components['tools'], components['handheld'])
    assert 'error' not in actual
    assert 'recipe' in actual
    assert actual['recipe'] == recipes_liquid[1]
    assert 'cost' in actual
    assert actual['cost'] == 5


def test_findBestRecipe_bothRecipesWork(recipes_liquid, inventory, skills, zone):
    # We choose the second recipe here since it has a lower endurance cost
    references = ['/1', '/3', '/4', '/6', '/9']
    skills.append(PlayerSkill(skill_name='smithing', skill_level=15))
    player = Player(
        id=100,
        equipped_weapon_id=2,
        inventory=inventory,
        skills=skills,
        zone=zone
    )
    components = separate_crafting_components(references, player)
    assert recipes_liquid[0].get_endurance_cost(player, components['tools'], components['handheld']) == 40
    actual = find_best_recipe(item_index.index['strange-liquid'], recipes_liquid, player,
            components['ingredients'], components['tools'], components['handheld'])
    assert 'error' not in actual
    assert 'recipe' in actual
    assert actual['recipe'] == recipes_liquid[1]
    assert 'cost' in actual
    assert actual['cost'] == 5


def test_findBestRecipe_missingIngredient(recipes_liquid, inventory, skills, zone):
    references = ['/1', '/9', '/6']
    player = Player(
        id=100,
        equipped_weapon_id=2,
        inventory=inventory,
        skills=skills,
        zone=zone
    )
    components = separate_crafting_components(references, player)
    actual = find_best_recipe(item_index.index['strange-liquid'], recipes_liquid[1:], player,
            components['ingredients'], components['tools'], components['handheld'])
    assert 'error' in actual
    assert actual['error'] == MESSAGE_MISSING_INGREDIENTS


def test_findBestRecipe_missingEmptyContainer(recipes_liquid, inventory, skills, zone):
    references = ['/1', '/3', '/6', '/4']
    player = Player(
        id=100,
        equipped_weapon_id=2,
        inventory=inventory,
        skills=skills,
        zone=zone
    )
    components = separate_crafting_components(references, player)
    actual = find_best_recipe(item_index.index['strange-liquid'], recipes_liquid[1:], player,
            components['ingredients'], components['tools'], components['handheld'])
    assert 'error' in actual
    assert actual['error'] == MESSAGE_EMPTY_CONTAINER


def test_findBestRecipe_missingSkills(recipes_liquid, inventory, skills, zone):
    references = ['/1', '/3', '/4', '/6', '/9']
    skills[0].skill_level = 10
    player = Player(
        id=100,
        equipped_weapon_id=2,
        inventory=inventory,
        skills=skills,
        zone=zone
    )
    components = separate_crafting_components(references, player)
    actual = find_best_recipe(item_index.index['strange-liquid'], recipes_liquid[1:], player,
            components['ingredients'], components['tools'], components['handheld'])
    assert 'error' in actual
    assert actual['error'] == MESSAGE_MISSING_SKILLS
