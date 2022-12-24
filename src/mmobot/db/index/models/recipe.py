from dataclasses import dataclass


@dataclass
class Recipe:
    products: list
    base_endurance: int
    ingredients: list
    tools: list
    handheld: str
    skills: dict

    def get_missing_ingredients(self, ingredients):
        '''
        From the given list of ingredients, returns a dict of ingredients missing
        from the recipe. If all ingredients are present, an empty list is returned.

        Args: ingredients - list of ItemInstances.
        '''
        ingredient_counter = self._get_ingredient_counter()
        for ingredient in ingredients:
            if ingredient.item_id in ingredient_counter:
                ingredient_counter[ingredient.item_id] -= 1
                if ingredient_counter[ingredient.item_id] == 0:
                    del ingredient_counter[ingredient.item_id]
        return ingredient_counter

    def get_crafting_skill(self, player_skills):
        '''
        Return a number from 0 to 70 representing the amount of surplus skill this player has
        for crafting this recipe. If the player does not have sufficient skills to craft the
        recipe, return -1.
        '''
        skill_count = len(self.skills)
        crafting_skill = 0
        for player_skill in player_skills:
            if player_skill.skill_name in self.skills:
                if player_skill.skill_level < self.skills[player_skill.skill_name]:
                    return -1
                crafting_skill += player_skill.skill_level - self.skills[player_skill.skill_name]
                skill_count -= 1
        if skill_count > 0:
            return -1
        return min(crafting_skill, 70)

    def from_yaml(item_id, yaml):
        endurance = yaml['endurance'] if 'endurance' in yaml else 0
        products = yaml['products'] if 'products' in yaml else [{'id': item_id, 'quantity': 1}]
        tools = yaml['tools'] if 'tools' in yaml else []
        handheld = yaml['handheld'] if 'handheld' in yaml else None
        skills = yaml['skills'] if 'skills' in yaml else {}
        return Recipe(
            products=products,
            base_endurance=endurance,
            ingredients=yaml['ingredients'],
            tools=tools,
            handheld=handheld,
            skills=skills
        )

    def _get_ingredient_counter(self):
        ingredient_counter = {}
        for ingredient in self.ingredients:
            ingredient_counter[ingredient['id']] = ingredient['quantity']
        return ingredient_counter
