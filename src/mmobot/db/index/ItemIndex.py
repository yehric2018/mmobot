import os
import yaml

from dotenv import load_dotenv

from mmobot.db.index.models import Recipe
from mmobot.db.models import (
    Arrow,
    Bow,
    FluidContainer,
    FluidFood,
    Poison,
    Resource,
    SolidFood,
    Tool,
    Weapon
)


load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')
DATA_PATH = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'index', 'data')


class ItemIndex:
    def __init__(self):
        self.index = {}
        self.recipes = {}
        self._setup_index()

    def load_to_database(self, session):
        for item in self.index:
            print(self.index[item])
            session.merge(self.index[item])
        session.commit()

    def get_recipes(item, yaml):
        recipes = []
        if 'recipes' in yaml:
            for recipe in yaml['recipes']:
                recipes.append(Recipe.from_yaml(item, recipe))
        return recipes

    def _setup_index(self):
        self._setup_items()
        self._setup_nonsolids()

    def _setup_items(self):
        self._setup_resources()
        self._setup_tools()
        self._setup_weapons()
        self._setup_bows()
        self._setup_arrows()
        self._setup_solid_food()
        self._setup_fluid_containers()

    def _setup_nonsolids(self):
        self._setup_fluid_food()
        self._setup_poisons()

    def _setup_resources(self):
        resources_path = os.path.join(DATA_PATH, 'items', 'resources')
        for resource_filename in os.listdir(resources_path):
            with open(os.path.join(resources_path, resource_filename), 'r') as f:
                try:
                    resource_yaml = yaml.safe_load(f)
                    resource = Resource.from_yaml(resource_yaml)
                    self.index[resource.id] = resource
                    self.recipes[resource.id] = ItemIndex.get_recipes(resource, resource_yaml)
                except yaml.YAMLError as exc:
                    print(exc)

    def _setup_tools(self):
        tools_path = os.path.join(DATA_PATH, 'items', 'tools')
        for tool_filename in os.listdir(tools_path):
            with open(os.path.join(tools_path, tool_filename), 'r') as f:
                try:
                    tool_yaml = yaml.safe_load(f)
                    tool = Tool.from_yaml(tool_yaml)
                    self.index[tool.id] = tool
                    self.recipes[tool.id] = ItemIndex.get_recipes(tool, tool_yaml)
                except yaml.YAMLError as exc:
                    print(exc)

    def _setup_weapons(self):
        weapons_path = os.path.join(DATA_PATH, 'items', 'weapons')
        for weapon_filename in os.listdir(weapons_path):
            with open(os.path.join(weapons_path, weapon_filename), 'r') as f:
                try:
                    weapon_yaml = yaml.safe_load(f)
                    weapon = Weapon.from_yaml(weapon_yaml)
                    self.index[weapon.id] = weapon
                    self.recipes[weapon.id] = ItemIndex.get_recipes(weapon, weapon_yaml)
                except yaml.YAMLError as exc:
                    print(exc)

    def _setup_bows(self):
        bows_path = os.path.join(DATA_PATH, 'items', 'bows')
        for bow_filename in os.listdir(bows_path):
            with open(os.path.join(bows_path, bow_filename), 'r') as f:
                try:
                    bow_yaml = yaml.safe_load(f)
                    bow = Bow.from_yaml(bow_yaml)
                    self.index[bow.id] = bow
                    self.recipes[bow.id] = ItemIndex.get_recipes(bow, bow_yaml)
                except yaml.YAMLError as exc:
                    print(exc)

    def _setup_arrows(self):
        arrows_path = os.path.join(DATA_PATH, 'items', 'arrows')
        for arrow_filename in os.listdir(arrows_path):
            with open(os.path.join(arrows_path, arrow_filename), 'r') as f:
                try:
                    arrow_yaml = yaml.safe_load(f)
                    arrow = Arrow.from_yaml(arrow_yaml)
                    self.index[arrow.id] = arrow
                    self.recipes[arrow.id] = ItemIndex.get_recipes(arrow, arrow_yaml)
                except yaml.YAMLError as exc:
                    print(exc)

    def _setup_solid_food(self):
        food_path = os.path.join(DATA_PATH, 'items', 'solid_foods')
        for food_filename in os.listdir(food_path):
            with open(os.path.join(food_path, food_filename), 'r') as f:
                try:
                    food_yaml = yaml.safe_load(f)
                    food = SolidFood.from_yaml(food_yaml)
                    self.index[food.id] = food
                    self.recipes[food.id] = ItemIndex.get_recipes(food, food_yaml)
                except yaml.YAMLError as exc:
                    print(exc)

    def _setup_fluid_containers(self):
        container_path = os.path.join(DATA_PATH, 'items', 'fluid_containers')
        for container_filename in os.listdir(container_path):
            with open(os.path.join(container_path, container_filename), 'r') as f:
                try:
                    container_yaml = yaml.safe_load(f)
                    container = FluidContainer.from_yaml(container_yaml)
                    self.index[container.id] = container
                    self.recipes[container.id] = ItemIndex.get_recipes(container, container_yaml)
                except yaml.YAMLError as exc:
                    print(exc)

    def _setup_fluid_food(self):
        food_path = os.path.join(DATA_PATH, 'nonsolids', 'fluid_foods')
        for food_filename in os.listdir(food_path):
            with open(os.path.join(food_path, food_filename), 'r') as f:
                try:
                    food_yaml = yaml.safe_load(f)
                    food = FluidFood.from_yaml(food_yaml)
                    self.index[food.id] = food
                    self.recipes[food.id] = ItemIndex.get_recipes(food, food_yaml)
                except yaml.YAMLError as exc:
                    print(exc)

    def _setup_poisons(self):
        poison_path = os.path.join(DATA_PATH, 'nonsolids', 'poisons')
        for poison_filename in os.listdir(poison_path):
            with open(os.path.join(poison_path, poison_filename), 'r') as f:
                try:
                    poison_yaml = yaml.safe_load(f)
                    self.index[poison_yaml['id']] = Poison.from_yaml(poison_yaml)
                except yaml.YAMLError as exc:
                    print(exc)
