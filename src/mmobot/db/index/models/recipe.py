from dataclasses import dataclass


MAX_EXTRA_SKILL = 70
EXTRA_SKILL_REDUCTION_SCALE = 0.01


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
        Return a number from 0 to MAX_EXTRA_SKILL representing the amount of surplus skill this
        player has for crafting this recipe. If the player does not have sufficient skills to craft
        the recipe, return -1.
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
        return min(crafting_skill, MAX_EXTRA_SKILL)

    def get_endurance_cost(self, player, tools=[], handheld=None, crafting_skill=None):
        '''
        Returns the endurance cost of crafting this recipe based on the given player's
        stats and skills, along with the tools/handhelds used for crafting the recipe. This
        computes the cost assuming that the correct ingredients are provided.

        Args:
            player - the player that will be doing the crafting
            tools - the list of tools provided for crafting
            handheld - the item the player currently has equipped
            crafting_skill - previously computed from the player's skills in the method above
        '''
        if crafting_skill is None:
            crafting_skill = self.get_crafting_skill(player.skills)
        assert crafting_skill >= 0
        endurance_cost = self.base_endurance
        for tool in tools:
            if tool.item.tool_type in self.tools:
                endurance_cost -= tool.item.craft
        if handheld is not None:
            endurance_cost -= handheld.item.craft
        skill_deduction = int(endurance_cost * EXTRA_SKILL_REDUCTION_SCALE * crafting_skill)
        return endurance_cost - skill_deduction

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
