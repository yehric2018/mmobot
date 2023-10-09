import pytest

from mmobot.db.index.models import Recipe
from mmobot.db.models import (
    ItemInstance,
    Player,
    PlayerSkill,
    Resource,
    SolidFood,
    SolidFoodInstance,
    Tool,
    ToolInstance,
    Weapon,
    WeaponInstance,
    Zone
)
from mmobot.test.db import init_test_engine
from mmobot.test.mock import MockItemIndex
from mmobot.utils.crafting import (
    create_item_instance,
    find_best_recipe,
    separate_crafting_components
)


engine = init_test_engine()


item_index = MockItemIndex()

MESSAGE_MISSING_INGREDIENTS = 'Missing ingredients for recipe(s).'
MESSAGE_EMPTY_CONTAINER = 'Missing empty container to store final contents.'
MESSAGE_MISSING_SKILLS = 'Insufficient skill to craft'


@pytest.fixture
def recipes_solid():
    stone_item = {'id': 'stone', 'quantity': 1}
    iron_item = {'id': 'iron-ore', 'quantity': 1}
    solid_item = Resource(id='solid-item', weight=2)
    return [
        Recipe.from_yaml(solid_item, {'ingredients': [stone_item], 'endurance': 20}),
        Recipe.from_yaml(solid_item, {'ingredients': [iron_item], 'endurance': 20})
    ]


@pytest.fixture
def inventory():
    return [
        ItemInstance(id=1, item_id='stone'),
        ItemInstance(id=3, item_id='iron-ore'),
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
    error_message = separate_crafting_components(references, None, None)
    assert error_message['error'] == 'nope'


def test_separateCraftingComponents_success(inventory, zone, skills):
    references = ['/7', '/1', '/2', '/5', '/3', '/6', '/4']
    player = Player(
        id=100,
        equipped_weapon_id=2,
        inventory=inventory,
        skills=skills,
        zone=zone.channel_name
    )
    components = separate_crafting_components(references, player, zone)
    assert 'error' not in components
    assert len(components['ingredients']) == 2
    assert inventory[0] in components['ingredients']
    assert inventory[1] in components['ingredients']
    assert inventory[2] not in components['ingredients']
    assert inventory[3] not in components['ingredients']
    assert len(components['tools']) == 1
    assert zone.loot[0] not in components['tools']
    assert zone.loot[1] in components['tools']
    assert zone.loot[2] not in components['tools']
    assert components['handheld'] is not None
    assert components['handheld'] == inventory[2]
    assert len(components['skills']) == 1
    assert components['skills'][0] == skills[0]


def test_findBestRecipe_successSolid(recipes_solid, inventory, skills, zone):
    references = ['/1', '/2']
    player = Player(
        id=100,
        equipped_weapon_id=2,
        inventory=inventory,
        skills=skills,
        zone=zone
    )
    components = separate_crafting_components(references, player, zone)
    actual = find_best_recipe(None, recipes_solid, player,
                              components['ingredients'],
                              components['tools'],
                              components['handheld'])
    assert 'error' not in actual
    assert 'recipe' in actual
    assert actual['recipe'] == recipes_solid[0]
    assert 'cost' in actual
    assert actual['cost'] == 20


def test_createItemInstance_weapon():
    instance = create_item_instance(Weapon(id='test'))
    assert isinstance(instance, WeaponInstance) is True
    assert instance.item_id == 'test'


def test_createItemInstance_tool():
    instance = create_item_instance(Tool(id='test'))
    assert isinstance(instance, ToolInstance) is True
    assert instance.item_id == 'test'


def test_createItemInstance_solidFood():
    instance = create_item_instance(SolidFood(id='test'))
    assert isinstance(instance, SolidFoodInstance) is True
    assert instance.item_id == 'test'


def test_createItemInstance_resource():
    instance = create_item_instance(Resource(id='test'))
    assert isinstance(instance, ItemInstance) is True
    assert isinstance(instance, WeaponInstance) is False
    assert isinstance(instance, ToolInstance) is False
    assert isinstance(instance, SolidFoodInstance) is False
    assert instance.item_id == 'test'
