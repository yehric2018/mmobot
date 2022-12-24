import os
import pytest
import yaml

from dotenv import load_dotenv

from mmobot.db.index.models import Recipe
from mmobot.db.models import (
    FluidContainer,
    FluidContainerInstance,
    ItemInstance,
    PlayerSkill,
    Tool,
    ToolInstance,
    Weapon,
    WeaponInstance
)
from mmobot.test.constants import (
    TEST_ITEM_ENTITY_NUMBER,
    TEST_PLAYER
)

load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')
DATA_PATH = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'index', 'data')

TEST_HANDAXE_FILEPATH = os.path.join(DATA_PATH, 'test', 'handaxe.yaml')
TEST_COIN_FILEPATH = os.path.join(DATA_PATH, 'test', 'copper-coin.yaml')
TEST_LIQUID_FILEPATH = os.path.join(DATA_PATH, 'test', 'strange-liquid.yaml')
TEST_ANVIL_FILEPATH = os.path.join(DATA_PATH, 'test', 'iron-anvil.yaml')
TEST_HAMMER_FILEPATH = os.path.join(DATA_PATH, 'test', 'iron-hammer.yaml')
TEST_BOWL_FILEPATH = os.path.join(DATA_PATH, 'test', 'stone-bowl.yaml')

TEST_HANDAXE_ID = 'handaxe'
TEST_HANDAXE_RECIPE_PRODUCT = {'id': TEST_HANDAXE_ID, 'type': 'item', 'quantity': 1}
TEST_HANDAXE_RECIPE_INGREDIENT = {'id': 'stone', 'quantity': 1}
TEST_HANDAXE_RECIPE_TOOLS = ['anvil']
TEST_HANDAXE_RECIPE_HANDHELD = 'hammer'
TEST_HANDAXE_RECIPE_ENDURANCE = 120
TEST_HANDAXE_RECIPE_SKILL_KNAPPING = 5
TEST_HANDAXE_INGREDIENT_LIST = [ItemInstance(id=TEST_ITEM_ENTITY_NUMBER, item_id='stone')]

TEST_COIN_ID = 'copper-coin'
TEST_COIN_RECIPE_PRODUCT = {'id': TEST_COIN_ID, 'type': 'item', 'quantity': 4}
TEST_COIN_RECIPE_INGREDIENT = {'id': 'copper-ingot', 'quantity': 1}
TEST_COIN_RECIPE_ENDRUANCE = 40
TEST_COIN_RECIPE_SKILL_SMITHING = 15
TEST_COIN_RECIPE_SKILL_COINING = 5

TEST_LIQUID_ID = 'strange-liquid'
TEST_LIQUID_RECIPE_PRODUCT = {'id': TEST_LIQUID_ID, 'type': 'nonsolid', 'quantity': 3}
TEST_LIQUID_RECIPE_INGREDIENT = {'id': 'water', 'quantity': 3}
TEST_LIQUID_RECIPE_ENDURANCE = 40
TEST_LIQUID_RECIPE_SKILL_SMITHING = 15


@pytest.fixture
def handaxe_yaml():
    with open(TEST_HANDAXE_FILEPATH, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


@pytest.fixture
def handaxe_recipe(handaxe_yaml):
    return Recipe.from_yaml(handaxe_yaml['id'], handaxe_yaml['recipes'][0])


@pytest.fixture
def coin_yaml():
    with open(TEST_COIN_FILEPATH, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


@pytest.fixture
def coin_recipe(coin_yaml):
    return Recipe.from_yaml(coin_yaml['id'], coin_yaml['recipes'][0])


@pytest.fixture
def liquid_yaml():
    with open(TEST_LIQUID_FILEPATH, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


@pytest.fixture
def liquid_recipe(liquid_yaml):
    return Recipe.from_yaml(liquid_yaml['id'], liquid_yaml['recipes'][0])


@pytest.fixture
def iron_anvil():
    with open(TEST_ANVIL_FILEPATH, 'r') as f:
        try:
            return Tool.from_yaml(yaml.safe_load(f))
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


@pytest.fixture
def iron_hammer():
    with open(TEST_HAMMER_FILEPATH, 'r') as f:
        try:
            return Weapon.from_yaml(yaml.safe_load(f))
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


@pytest.fixture
def stone_bowl():
    with open(TEST_BOWL_FILEPATH, 'r') as f:
        try:
            return FluidContainer.from_yaml(yaml.safe_load(f))
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


@pytest.fixture
def coin_crafter_skills():
    return [
        PlayerSkill(skill_name='smithing', skill_level=TEST_COIN_RECIPE_SKILL_SMITHING),
        PlayerSkill(skill_name='coining', skill_level=TEST_COIN_RECIPE_SKILL_COINING)
    ]


@pytest.fixture
def handaxe_crafter():
    player = TEST_PLAYER
    player.skills = [
        PlayerSkill(skill_name='knapping', skill_level=TEST_HANDAXE_RECIPE_SKILL_KNAPPING)
    ]
    return player


def test_Recipe_fromYaml_simpleRecipe(handaxe_yaml):
    recipe = Recipe.from_yaml(handaxe_yaml['id'], handaxe_yaml['recipes'][0])
    assert recipe.base_endurance == TEST_HANDAXE_RECIPE_ENDURANCE
    assert len(recipe.products) == 1
    assert recipe.products[0] == TEST_HANDAXE_RECIPE_PRODUCT
    assert len(recipe.ingredients) == 1
    assert recipe.ingredients[0] == TEST_HANDAXE_RECIPE_INGREDIENT
    assert recipe.tools == TEST_HANDAXE_RECIPE_TOOLS
    assert recipe.handheld == TEST_HANDAXE_RECIPE_HANDHELD
    assert len(recipe.skills) == 1
    assert recipe.skills['knapping'] == TEST_HANDAXE_RECIPE_SKILL_KNAPPING


def test_Recipe_fromYaml_withProducts_noToolsOrHandhelds(coin_yaml):
    recipe = Recipe.from_yaml(coin_yaml['id'], coin_yaml['recipes'][0])
    assert len(recipe.products) == 1
    assert recipe.products[0] == TEST_COIN_RECIPE_PRODUCT
    assert len(recipe.ingredients) == 1
    assert recipe.ingredients[0] == TEST_COIN_RECIPE_INGREDIENT
    assert len(recipe.tools) == 0
    assert recipe.handheld is None
    assert len(recipe.skills) == 2
    assert recipe.skills['smithing'] == 15
    assert recipe.skills['coining'] == 5


def test_Recipe_fromYaml_nonsolid(liquid_yaml):
    recipe = Recipe.from_yaml(liquid_yaml['id'], liquid_yaml['recipes'][0])
    assert recipe.base_endurance == TEST_LIQUID_RECIPE_ENDURANCE
    assert len(recipe.products) == 1
    assert recipe.products[0] == TEST_LIQUID_RECIPE_PRODUCT
    assert len(recipe.ingredients) == 1
    assert recipe.ingredients[0] == TEST_LIQUID_RECIPE_INGREDIENT
    assert len(recipe.tools) == 0
    assert recipe.handheld is None
    assert len(recipe.skills) == 1
    assert recipe.skills['smithing'] == 15


def test_Recipe_getMissingIngredients_matchReturnsEmpty(handaxe_recipe):
    assert len(handaxe_recipe.get_missing_ingredients(TEST_HANDAXE_INGREDIENT_LIST)) == 0


def test_Recipe_getMissingIngredients_missingIngredientReturnsNonempty(handaxe_recipe):
    missing_ingredients = handaxe_recipe.get_missing_ingredients([])
    assert len(missing_ingredients) == 1
    assert missing_ingredients['stone'] == 1


def test_Recipe_getMissingIngredients_surplusIngredientsReturnsEmpty(handaxe_recipe):
    ingredients = TEST_HANDAXE_INGREDIENT_LIST + [ItemInstance(id=50, item_id='stone')]
    assert len(handaxe_recipe.get_missing_ingredients(ingredients)) == 0


def test_Recipe_getMissingIngredients_nonsolidMatch(liquid_recipe):
    ingredient_list = [
        FluidContainerInstance(id='stone-bowl', nonsolid_id='water', units=3)
    ]
    assert len(liquid_recipe.get_missing_ingredients(ingredient_list)) == 0


def test_Recipe_getMissingIngredients_nonsolidMissingIngredient(liquid_recipe):
    ingredient_list = []
    missing_ingredients = liquid_recipe.get_missing_ingredients(ingredient_list)
    assert len(missing_ingredients) == 1
    assert missing_ingredients['water'] == 3


def test_Recipe_getMissingIngredients_nonsolidNotEnoughLiquid(liquid_recipe):
    ingredient_list = [
        FluidContainerInstance(id='stone-bowl', nonsolid_id='water', units=2)
    ]
    missing_ingredients = liquid_recipe.get_missing_ingredients(ingredient_list)
    assert len(missing_ingredients) == 1
    assert missing_ingredients['water'] == 1


def test_Recipe_getMissingIngredients_nonsolidSplitAcrossContainers(liquid_recipe):
    ingredient_list = [
        FluidContainerInstance(id='stone-bowl', nonsolid_id='water', units=2),
        FluidContainerInstance(id='stone-bowl-2', nonsolid_id='water', units=2)
    ]
    assert len(liquid_recipe.get_missing_ingredients(ingredient_list)) == 0


def test_Recipe_isMissingContainer_solid(coin_recipe):
    assert coin_recipe.is_missing_container([]) is False


def test_Recipe_isMissingContainer_nonsolidHasContainer(liquid_recipe, stone_bowl):
    ingredient_list = [
        FluidContainerInstance(id='stone-bowl', item=stone_bowl, nonsolid_id='water', units=2),
        FluidContainerInstance(id='stone-bowl-2', item=stone_bowl, nonsolid_id=None, units=0)
    ]
    assert liquid_recipe.is_missing_container(ingredient_list) is False


def test_Recipe_isMissingContainer_nonsolidHasNoContainer(liquid_recipe, stone_bowl):
    ingredient_list = [
        FluidContainerInstance(id='stone-bowl', item=stone_bowl, nonsolid_id='water', units=2),
        FluidContainerInstance(id='stone-bowl-2', item=stone_bowl, nonsolid_id='water', units=2)
    ]
    assert liquid_recipe.is_missing_container(ingredient_list) is True


def test_Recipe_getCraftingSkill_barelySufficientSkill(coin_recipe, coin_crafter_skills):
    assert coin_recipe.get_crafting_skill(coin_crafter_skills) == 0


def test_Recipe_getCraftingSkill_insufficientSkill(coin_recipe, coin_crafter_skills):
    assert coin_recipe.get_crafting_skill(coin_crafter_skills[:1]) == -1


def test_Recipe_getCraftingSkill_surplusSkill(coin_recipe, coin_crafter_skills):
    coin_crafter_skills[0].skill_level = 50
    coin_crafter_skills[1].skill_level = 10
    assert coin_recipe.get_crafting_skill(coin_crafter_skills) == 40


def test_Recipe_getEnduranceCost_minimumComponents(handaxe_recipe, handaxe_crafter):
    assert handaxe_recipe.get_endurance_cost(handaxe_crafter) == 120


def test_Recipe_getEnduranceCost_provideTool(iron_anvil, handaxe_recipe, handaxe_crafter):
    tools = [ToolInstance(id=1, item=iron_anvil)]
    assert handaxe_recipe.get_endurance_cost(handaxe_crafter, tools=tools) == 100


def test_Recipe_getEnduranceCost_provideHandheld(iron_hammer, handaxe_recipe, handaxe_crafter):
    weapon = WeaponInstance(id=1, item=iron_hammer)
    assert handaxe_recipe.get_endurance_cost(handaxe_crafter, handheld=weapon) == 45


def test_Recipe_getEnduranceCost_extraSkill(coin_recipe, coin_crafter_skills, handaxe_crafter):
    coin_crafter_skills[0].skill_level = 50
    coin_crafter_skills[1].skill_level = 10
    handaxe_crafter.skills = coin_crafter_skills
    assert coin_recipe.get_endurance_cost(handaxe_crafter) == 24
