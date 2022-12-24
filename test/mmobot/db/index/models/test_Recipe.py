import os
import pytest
import yaml

from dotenv import load_dotenv

from mmobot.db.index.models import Recipe
from mmobot.db.models import ItemInstance, PlayerSkill
from mmobot.test.constants import TEST_ITEM_ENTITY_NUMBER

load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')
DATA_PATH = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'index', 'data')

TEST_HANDAXE_FILEPATH = os.path.join(DATA_PATH, 'test', 'handaxe.yaml')
TEST_COIN_FILEPATH = os.path.join(DATA_PATH, 'test', 'copper-coin.yaml')

TEST_HANDAXE_ID = 'handaxe'
TEST_HANDAXE_RECIPE_PRODUCT = {'id': TEST_HANDAXE_ID, 'quantity': 1}
TEST_HANDAXE_RECIPE_INGREDIENT = {'id': 'stone', 'quantity': 1}
TEST_HANDAXE_RECIPE_TOOLS = ['anvil']
TEST_HANDAXE_RECIPE_HANDHELD = 'knife'
TEST_HANDAXE_RECIPE_ENDURANCE = 70
TEST_HANDAXE_RECIPE_SKILL_KNAPPING = 5

TEST_COIN_ID = 'copper-coin'
TEST_COIN_RECIPE_PRODUCT = {'id': TEST_COIN_ID, 'quantity': 4}
TEST_COIN_RECIPE_INGREDIENT = {'id': 'copper-ingot', 'quantity': 1}
TEST_COIN_RECIPE_ENDRUANCE = 40
TEST_COIN_RECIPE_SKILL_SMITHING = 15
TEST_COIN_RECIPE_SKILL_COINING = 5

TEST_HANDAXE_INGREDIENT_LIST = [ItemInstance(id=TEST_ITEM_ENTITY_NUMBER, item_id='stone')]


@pytest.fixture
def handaxe_yaml():
    with open(TEST_HANDAXE_FILEPATH, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


@pytest.fixture
def coin_yaml():
    with open(TEST_COIN_FILEPATH, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


@pytest.fixture
def coin_crafter_skills():
    return [
        PlayerSkill(skill_name='smithing', skill_level=TEST_COIN_RECIPE_SKILL_SMITHING),
        PlayerSkill(skill_name='coining', skill_level=TEST_COIN_RECIPE_SKILL_COINING)
    ]


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


def test_Recipe_getMissingIngredients_matchReturnsEmpty(handaxe_yaml):
    recipe = Recipe.from_yaml(handaxe_yaml['id'], handaxe_yaml['recipes'][0])
    assert len(recipe.get_missing_ingredients(TEST_HANDAXE_INGREDIENT_LIST)) == 0


def test_Recipe_getMissingIngredients_missingIngredientReturnsNonempty(handaxe_yaml):
    recipe = Recipe.from_yaml(handaxe_yaml['id'], handaxe_yaml['recipes'][0])
    missing_ingredients = recipe.get_missing_ingredients([])
    assert len(missing_ingredients) == 1
    assert missing_ingredients['stone'] == 1


def test_Recipe_getMissingIngredients_surplusIngredientsReturnsEmpty(handaxe_yaml):
    recipe = Recipe.from_yaml(handaxe_yaml['id'], handaxe_yaml['recipes'][0])
    ingredients = TEST_HANDAXE_INGREDIENT_LIST + [ItemInstance(id=50, item_id='stone')]
    assert len(recipe.get_missing_ingredients(ingredients)) == 0


def test_Recipe_getCraftingSkill_barelySufficientSkill(coin_yaml, coin_crafter_skills):
    recipe = Recipe.from_yaml(coin_yaml['id'], coin_yaml['recipes'][0])
    assert recipe.get_crafting_skill(coin_crafter_skills) == 0


def test_Recipe_getCraftingSkill_insufficientSkill(coin_yaml, coin_crafter_skills):
    recipe = Recipe.from_yaml(coin_yaml['id'], coin_yaml['recipes'][0])
    assert recipe.get_crafting_skill(coin_crafter_skills[:1]) == -1


def test_Recipe_getCraftingSkill_surplusSkill(coin_yaml, coin_crafter_skills):
    coin_crafter_skills[0].skill_level = 50
    coin_crafter_skills[1].skill_level = 10
    recipe = Recipe.from_yaml(coin_yaml['id'], coin_yaml['recipes'][0])
    assert recipe.get_crafting_skill(coin_crafter_skills) == 40
