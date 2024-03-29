import os
import pytest
import yaml

from dotenv import load_dotenv

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
    WeaponInstance
)
from mmobot.test.constants import (
    TEST_ITEM_ENTITY_NUMBER,
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
TEST_HANDAXE_INGREDIENT_LIST = [
    ItemInstance(id=TEST_ITEM_ENTITY_NUMBER, item_id='stone', item=Resource(weight=5))
]

TEST_COIN_ID = 'copper-coin'
TEST_COIN_RECIPE_PRODUCT = {'id': TEST_COIN_ID, 'type': 'item', 'quantity': 4}
TEST_COIN_RECIPE_INGREDIENT = {'id': 'copper-ingot', 'quantity': 1}
TEST_COIN_RECIPE_ENDRUANCE = 40
TEST_COIN_RECIPE_SKILL_SMITHING = 15
TEST_COIN_RECIPE_SKILL_COINING = 5


@pytest.fixture
def handaxe_yaml():
    with open(TEST_HANDAXE_FILEPATH, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


@pytest.fixture
def handaxe(handaxe_yaml):
    return Weapon.from_yaml(handaxe_yaml)


@pytest.fixture
def handaxe_recipe(handaxe, handaxe_yaml):
    return Recipe.from_yaml(handaxe, handaxe_yaml['recipes'][0])


@pytest.fixture
def coin_yaml():
    with open(TEST_COIN_FILEPATH, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


@pytest.fixture
def coin(coin_yaml):
    return Resource.from_yaml(coin_yaml)


@pytest.fixture
def coin_recipe(coin, coin_yaml):
    return Recipe.from_yaml(coin, coin_yaml['recipes'][0])


@pytest.fixture
def liquid_yaml():
    with open(TEST_LIQUID_FILEPATH, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


@pytest.fixture
def liquid_recipe(liquid, liquid_yaml):
    return Recipe.from_yaml(liquid, liquid_yaml['recipes'][0])


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
def coin_crafter_skills():
    return [
        PlayerSkill(skill_name='smithing', skill_level=TEST_COIN_RECIPE_SKILL_SMITHING),
        PlayerSkill(skill_name='coining', skill_level=TEST_COIN_RECIPE_SKILL_COINING)
    ]


@pytest.fixture
def handaxe_crafter():
    return Player(
        hp=100, endurance=100,
        skills=[
            PlayerSkill(skill_name='knapping', skill_level=TEST_HANDAXE_RECIPE_SKILL_KNAPPING)
        ],
        inventory=[] + TEST_HANDAXE_INGREDIENT_LIST,
        inventory_weight=5
    )


def test_Recipe_fromYaml_simpleRecipe(handaxe, handaxe_yaml):
    recipe = Recipe.from_yaml(handaxe, handaxe_yaml['recipes'][0])
    assert recipe.base_endurance == TEST_HANDAXE_RECIPE_ENDURANCE
    assert recipe.product is not None
    assert recipe.product == handaxe
    assert len(recipe.ingredients) == 1
    assert recipe.ingredients[0] == TEST_HANDAXE_RECIPE_INGREDIENT
    assert recipe.tools == TEST_HANDAXE_RECIPE_TOOLS
    assert recipe.handheld == TEST_HANDAXE_RECIPE_HANDHELD
    assert len(recipe.skills) == 1
    assert recipe.skills['knapping'] == TEST_HANDAXE_RECIPE_SKILL_KNAPPING


def test_Recipe_fromYaml_withProducts_noToolsOrHandhelds(coin, coin_yaml):
    recipe = Recipe.from_yaml(coin, coin_yaml['recipes'][0])
    assert recipe.product == coin
    assert recipe.quantity == 4
    assert len(recipe.ingredients) == 1
    assert recipe.ingredients[0] == TEST_COIN_RECIPE_INGREDIENT
    assert len(recipe.tools) == 0
    assert recipe.handheld is None
    assert len(recipe.skills) == 2
    assert recipe.skills['smithing'] == 15
    assert recipe.skills['coining'] == 5


def test_Recipe_getMissingIngredients_matchReturnsEmpty(handaxe_recipe):
    assert len(handaxe_recipe.get_missing_ingredients(TEST_HANDAXE_INGREDIENT_LIST)) == 0


def test_Recipe_getMissingIngredients_missingIngredientReturnsNonempty(handaxe_recipe):
    missing_ingredients = handaxe_recipe.get_missing_ingredients([])
    assert len(missing_ingredients) == 1
    assert missing_ingredients['stone'] == 1


def test_Recipe_getMissingIngredients_surplusIngredientsReturnsEmpty(handaxe_recipe):
    ingredients = TEST_HANDAXE_INGREDIENT_LIST + [ItemInstance(id=50, item_id='stone')]
    assert len(handaxe_recipe.get_missing_ingredients(ingredients)) == 0


def test_Recipe_isMissingContainer_solid(coin_recipe):
    assert coin_recipe.is_missing_container([]) is False


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


def test_Recipe_getEnduranceCost_handheldWrongType(handaxe, handaxe_recipe, handaxe_crafter):
    weapon = WeaponInstance(id=1, item=handaxe)
    assert handaxe_recipe.get_endurance_cost(handaxe_crafter, handheld=weapon) == 120


def test_Recipe_getEnduranceCost_extraSkill(coin_recipe, coin_crafter_skills, handaxe_crafter):
    coin_crafter_skills[0].skill_level = 50
    coin_crafter_skills[1].skill_level = 10
    handaxe_crafter.skills = coin_crafter_skills
    assert coin_recipe.get_endurance_cost(handaxe_crafter) == 24


def test_Recipe_apply_weaponRecipeNoCost(handaxe_crafter, handaxe_recipe):
    handaxe_recipe.apply(handaxe_crafter, 0, ingredients=TEST_HANDAXE_INGREDIENT_LIST)
    assert handaxe_crafter.hp == 100
    assert handaxe_crafter.endurance == 100
    assert len(handaxe_crafter.inventory) == 2
    assert handaxe_crafter.inventory[0].owner_id is None
    assert handaxe_crafter.inventory[1].item_id == TEST_HANDAXE_ID
    assert isinstance(handaxe_crafter.inventory[1], WeaponInstance)
    assert handaxe_crafter.inventory_weight == 3


def test_Recipe_apply_recipeWithCost(handaxe_crafter, handaxe_recipe):
    handaxe_recipe.apply(handaxe_crafter, 40, ingredients=TEST_HANDAXE_INGREDIENT_LIST)
    assert handaxe_crafter.hp == 100
    assert handaxe_crafter.endurance == 60
    assert len(handaxe_crafter.inventory) == 2
    assert handaxe_crafter.inventory[0].owner_id is None
    assert handaxe_crafter.inventory[1].item_id == TEST_HANDAXE_ID
    assert isinstance(handaxe_crafter.inventory[1], WeaponInstance)
    assert handaxe_crafter.inventory_weight == 3


def test_Recipe_apply_recipeWithHPCost(handaxe_crafter, handaxe_recipe):
    handaxe_recipe.apply(handaxe_crafter, 140, ingredients=TEST_HANDAXE_INGREDIENT_LIST)
    assert handaxe_crafter.hp == 60
    assert handaxe_crafter.endurance == 0
    assert len(handaxe_crafter.inventory) == 2
    assert handaxe_crafter.inventory[0].owner_id is None
    assert handaxe_crafter.inventory[1].item_id == TEST_HANDAXE_ID
    assert isinstance(handaxe_crafter.inventory[1], WeaponInstance)
    assert handaxe_crafter.inventory_weight == 3


def test_Recipe_apply_toolRecipe(handaxe_crafter, handaxe_recipe):
    handaxe_recipe.product = Tool(id=TEST_HANDAXE_ID, weight=3)
    handaxe_recipe.apply(handaxe_crafter, 40, ingredients=TEST_HANDAXE_INGREDIENT_LIST)
    assert handaxe_crafter.hp == 100
    assert handaxe_crafter.endurance == 60
    assert len(handaxe_crafter.inventory) == 2
    assert handaxe_crafter.inventory[0].owner_id is None
    assert handaxe_crafter.inventory[1].item_id == TEST_HANDAXE_ID
    assert isinstance(handaxe_crafter.inventory[1], ToolInstance)
    assert handaxe_crafter.inventory_weight == 3


def test_Recipe_apply_solidFoodRecipe(handaxe_crafter, handaxe_recipe):
    handaxe_recipe.product = SolidFood(id=TEST_HANDAXE_ID, weight=3)
    handaxe_recipe.apply(handaxe_crafter, 40, ingredients=TEST_HANDAXE_INGREDIENT_LIST)
    assert handaxe_crafter.hp == 100
    assert handaxe_crafter.endurance == 60
    assert len(handaxe_crafter.inventory) == 2
    assert handaxe_crafter.inventory[0].owner_id is None
    assert handaxe_crafter.inventory[1].item_id == TEST_HANDAXE_ID
    assert isinstance(handaxe_crafter.inventory[1], SolidFoodInstance)
    assert handaxe_crafter.inventory_weight == 3


def test_Recipe_apply_resourceRecipe(handaxe_crafter, handaxe_recipe):
    handaxe_recipe.product = Resource(id=TEST_HANDAXE_ID, weight=3)
    handaxe_recipe.apply(handaxe_crafter, 40, ingredients=TEST_HANDAXE_INGREDIENT_LIST)
    assert handaxe_crafter.hp == 100
    assert handaxe_crafter.endurance == 60
    assert len(handaxe_crafter.inventory) == 2
    assert handaxe_crafter.inventory[0].owner_id is None
    assert handaxe_crafter.inventory[1].item_id == TEST_HANDAXE_ID
    assert isinstance(handaxe_crafter.inventory[1], ItemInstance)
    assert not isinstance(handaxe_crafter.inventory[1], WeaponInstance)
    assert not isinstance(handaxe_crafter.inventory[1], ToolInstance)
    assert not isinstance(handaxe_crafter.inventory[1], SolidFoodInstance)
    assert handaxe_crafter.inventory_weight == 3


def test_Recipe_apply_recipeWithQuantity(handaxe_crafter, handaxe_recipe):
    handaxe_recipe.quantity = 4
    handaxe_recipe.apply(handaxe_crafter, 40, ingredients=TEST_HANDAXE_INGREDIENT_LIST)
    assert handaxe_crafter.hp == 100
    assert handaxe_crafter.endurance == 60
    assert len(handaxe_crafter.inventory) == 5
    assert handaxe_crafter.inventory[0].owner_id is None
    for i in range(1, 5):
        assert handaxe_crafter.inventory[i].item_id == TEST_HANDAXE_ID
        assert isinstance(handaxe_crafter.inventory[1], WeaponInstance)
    assert handaxe_crafter.inventory_weight == 12
