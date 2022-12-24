import os
import yaml

from dotenv import load_dotenv

from mmobot.db.index.models import Recipe

load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')
DATA_PATH = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'index', 'data')

TEST_HANDAXE_ID = 'handaxe'
TEST_HANDAXE_RECIPE_PRODUCT = {'id': TEST_HANDAXE_ID, 'quantity': 1}
TEST_HANDAXE_RECIPE_INGREDIENT = {'id': 'stone', 'quantity': 1}
TEST_HANDAXE_RECIPE_TOOLS = ['anvil']
TEST_HANDAXE_RECIPE_HANDHELD = 'knife'
TEST_HANDAXE_RECIPE_ENDURANCE = 70
TEST_HANDAXE_RECIPE_SKILL = {'name': 'knapping', 'level': 5}

TEST_COIN_ID = 'copper-coin'
TEST_COIN_RECIPE_PRODUCT = {'id': TEST_COIN_ID, 'quantity': 4}
TEST_COIN_RECIPE_INGREDIENT = {'id': 'copper-ingot', 'quantity': 1}
TEST_COIN_RECIPE_ENDRUANCE = 40
TEST_COIN_RECIPE_SKILL_SMITHING = {'name': 'smithing', 'level': 15}
TEST_COIN_RECIPE_SKILL_COINING = {'name': 'coining', 'level': 5}


def test_Recipe_fromYaml_simpleRecipe():
    with open(os.path.join(DATA_PATH, 'test', 'handaxe.yaml'), 'r') as f:
        try:
            weapon_yaml = yaml.safe_load(f)
            recipe = Recipe.from_yaml(weapon_yaml['id'], weapon_yaml['recipes'][0])
            assert recipe.base_endurance == TEST_HANDAXE_RECIPE_ENDURANCE
            assert len(recipe.products) == 1
            assert recipe.products[0] == TEST_HANDAXE_RECIPE_PRODUCT
            assert len(recipe.ingredients) == 1
            assert recipe.ingredients[0] == TEST_HANDAXE_RECIPE_INGREDIENT
            assert recipe.tools == TEST_HANDAXE_RECIPE_TOOLS
            assert recipe.handheld == TEST_HANDAXE_RECIPE_HANDHELD
            assert len(recipe.skills) == 1
            assert recipe.skills[0] == TEST_HANDAXE_RECIPE_SKILL
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False


def test_Recipe_fromYaml_withProducts_noToolsOrHandhelds():
    with open(os.path.join(DATA_PATH, 'test', 'copper-coin.yaml'), 'r') as f:
        try:
            coin_yaml = yaml.safe_load(f)
            recipe = Recipe.from_yaml(coin_yaml['id'], coin_yaml['recipes'][0])
            assert len(recipe.products) == 1
            assert recipe.products[0] == TEST_COIN_RECIPE_PRODUCT
            assert len(recipe.ingredients) == 1
            assert recipe.ingredients[0] == TEST_COIN_RECIPE_INGREDIENT
            assert len(recipe.tools) == 0
            assert recipe.handheld is None
            assert len(recipe.skills) == 2
            assert TEST_COIN_RECIPE_SKILL_SMITHING in recipe.skills
            assert TEST_COIN_RECIPE_SKILL_COINING in recipe.skills
        except yaml.YAMLError as exc:
            assert f'Encountered yaml error: {exc}' is False
