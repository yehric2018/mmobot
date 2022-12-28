from dataclasses import dataclass

from mmobot.db.models import (
    Item,
    FluidContainerInstance,
    Nonsolid,
)
from mmobot.utils.crafting import create_item_instance


TYPE_ITEM = 'item'
TYPE_NONSOLID = 'nonsolid'

MAX_EXTRA_SKILL = 70
EXTRA_SKILL_REDUCTION_SCALE = 0.01


@dataclass
class Recipe:
    product: Item
    quantity: int
    side_products: list
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
            elif (isinstance(ingredient, FluidContainerInstance)
                    and ingredient.nonsolid_id in ingredient_counter):
                ingredient_counter[ingredient.nonsolid_id] -= ingredient.units
                if ingredient_counter[ingredient.nonsolid_id] <= 0:
                    del ingredient_counter[ingredient.nonsolid_id]
        return ingredient_counter

    def is_missing_container(self, ingredients):
        '''
        Returns False if this recipe is not for a nonsolid, or if the ingredients list
        includes an empty container with enough space for the product. If it is a nonsolid
        recipe that doesn't provide such a container, return True.

        TODO: Might be good to add some logic here later to account for nonsolids in the
        list of extra products.

        Args: ingredients - list of ItemInstances.
        '''
        return (isinstance(self.product, Nonsolid)
                and self._find_compatible_container(ingredients) is None)

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
        if handheld is not None and handheld.item.weapon_type == self.handheld:
            endurance_cost -= handheld.item.craft
        skill_deduction = int(endurance_cost * EXTRA_SKILL_REDUCTION_SCALE * crafting_skill)
        return endurance_cost - skill_deduction

    def apply(self, player, endurance_cost, ingredients=[], tools=[], handheld=None):
        '''
        Apply this recipe, which will do the following:
        - Reduce the endurance (and maybe HP) of the player by endurance_cost
        - Remove all the current items in the player's inventory
        - TODO: Reduce the remaining uses/condition of all the tools and handheld used, handle
          breaking of items
        - Add the newly created item(s) to the player's inventory
        Calling this method assumes the following have already been asserted:
        - All the necessary ingredients are in the player's inventory
        - The player has sufficient skill to craft the recipe
        - The given endurance_cost was already calculated

        Args:
            session - current database session
            player - the player that will be doing the crafting
            item_index
            endurance_cost - precomputed from Recipe.get_endurance_cost
            tools - the list of tools provided for crafting
            handheld - the item the player currently has equipped
        '''
        actual_endurance_cost = min(endurance_cost, player.endurance)
        hp_cost = endurance_cost - actual_endurance_cost
        player.endurance -= actual_endurance_cost
        player.hp -= hp_cost

        if isinstance(self.product, Nonsolid):
            container = self._find_compatible_container(ingredients)
            container.nonsolid_id = self.product.id
            container.units = self.quantity
        else:
            product_instance = create_item_instance(self.product)
            for _ in range(self.quantity):
                player.inventory.append(product_instance)

        ingredient_counter = self._get_ingredient_counter()
        for item_instance in ingredients:
            if item_instance.item_id in ingredient_counter:
                item_id = item_instance.item_id
                item_instance.player_id = None
                ingredient_counter[item_id] -= 1
                if ingredient_counter[item_id] == 0:
                    del ingredient_counter[item_id]
            elif (isinstance(item_instance, FluidContainerInstance)
                    and item_instance.nonsolid_id in ingredient_counter):
                nonsolid_id = item_instance.nonsolid_id
                units_used = min(
                    item_instance.units,
                    ingredient_counter[nonsolid_id]
                )
                item_instance.units -= units_used
                ingredient_counter[nonsolid_id] -= units_used
                if item_instance.units == 0:
                    item_instance.nonsolid_id = None
                if ingredient_counter[nonsolid_id] == 0:
                    del ingredient_counter[nonsolid_id]
        assert len(ingredient_counter) == 0

    def from_yaml(item, yaml):
        endurance = yaml['endurance'] if 'endurance' in yaml else 0
        quantity = yaml['quantity'] if 'quantity' in yaml else 1
        side_products = yaml['side_products'] if 'side_products' in yaml else []
        tools = yaml['tools'] if 'tools' in yaml else []
        handheld = yaml['handheld'] if 'handheld' in yaml else None
        skills = yaml['skills'] if 'skills' in yaml else {}
        return Recipe(
            product=item,
            quantity=quantity,
            side_products=side_products,
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

    def _find_compatible_container(self, ingredients):
        '''
        Returns the first empty container in the inventory that can hold the product of
        this recipe. Returns None if no container is found (this should never happen if we
        ran is_missing_container before).
        '''
        if isinstance(self.product, Nonsolid):
            for ingredient in ingredients:
                if (isinstance(ingredient, FluidContainerInstance) and ingredient.units == 0
                        and ingredient.item.max_capacity >= self.quantity):
                    return ingredient
        return None
