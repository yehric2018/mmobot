from dataclasses import dataclass


@dataclass
class Recipe:
    products: list
    base_endurance: int
    ingredients: list
    tools: list
    handheld: str
    skills: list

    def ingredients_match(self, ingredients):
        ingredient_map = {}
        for ingredient in self.ingredients:
            if ingredient.name not in ingredient_map:
                ingredient_map[ingredient.name] = 0

    def can_craft(self, player, ingredients=[], tools=[], containers=[], handheld=None):
        pass

    def from_yaml(item_id, yaml):
        endurance = yaml['endurance'] if 'endurance' in yaml else 0
        products = yaml['products'] if 'products' in yaml else [{'id': item_id, 'quantity': 1}]
        tools = yaml['tools'] if 'tools' in yaml else []
        handheld = yaml['handheld'] if 'handheld' in yaml else None
        skills = yaml['skills'] if 'skills' in yaml else []
        return Recipe(
            products=products,
            base_endurance=endurance,
            ingredients=yaml['ingredients'],
            tools=tools,
            handheld=handheld,
            skills=skills
        )
