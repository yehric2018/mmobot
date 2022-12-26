import os
import yaml

from dotenv import load_dotenv

from mmobot.db.index import ItemIndex
from mmobot.db.models import (
    FluidContainer,
    FluidFood,
    Resource,
    Tool,
    Weapon
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


class MockItemIndex(ItemIndex):
    def __init__(self):
        self.index = {}
        self.recipes = {}
        self._setup_index()

        for item in self.index:
            print(self.index[item])

    def _setup_index(self):
        handaxe = self._load_yaml(TEST_HANDAXE_FILEPATH)
        self.index[handaxe['id']] = Weapon.from_yaml(handaxe)
        self.recipes[handaxe['id']] = ItemIndex._get_recipes(self.index[handaxe['id']], handaxe)

        coin = self._load_yaml(TEST_COIN_FILEPATH)
        self.index[coin['id']] = Resource.from_yaml(coin)
        self.recipes[coin['id']] = ItemIndex._get_recipes(self.index[coin['id']], coin)

        liquid = self._load_yaml(TEST_LIQUID_FILEPATH)
        self.index[liquid['id']] = FluidFood.from_yaml(liquid)
        self.recipes[liquid['id']] = ItemIndex._get_recipes(self.index[liquid['id']], liquid)

        anvil = self._load_yaml(TEST_ANVIL_FILEPATH)
        self.index[anvil['id']] = Tool.from_yaml(anvil)
        self.recipes[anvil['id']] = ItemIndex._get_recipes(self.index[anvil['id']], anvil)

        hammer = self._load_yaml(TEST_HAMMER_FILEPATH)
        self.index[hammer['id']] = Weapon.from_yaml(hammer)
        self.recipes[hammer['id']] = ItemIndex._get_recipes(self.index[hammer['id']], hammer)

        bowl = self._load_yaml(TEST_BOWL_FILEPATH)
        self.index[bowl['id']] = FluidContainer.from_yaml(bowl)
        self.recipes[bowl['id']] = ItemIndex._get_recipes(self.index[bowl['id']], bowl)

    def _load_yaml(self, filepath):
        with open(filepath, 'r') as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)
