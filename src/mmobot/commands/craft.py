from sqlalchemy.orm import Session

from mmobot.db.models import Nonsolid, Player
from mmobot.utils.crafting import find_best_recipe, separate_crafting_components


async def craft_logic(context, args, engine, item_index, use_hp=False):
    if context.channel.category.name != 'World':
        return
    
    goal_item_id = args[0]
    discord_id = context.author.id
    if goal_item_id not in item_index.index:
        await context.send(f'<@{discord_id}> {goal_item_id} does not exist.')
        return
    elif len(item_index.recipes[goal_item_id]) == 0:
        await context.send(f'<@{discord_id}> You cannot craft {goal_item_id}.')
        return
    
    goal_item = item_index.items[goal_item_id]
    with Session(engine) as session:
        player = Player.select_with_discord_id(session, discord_id)
        assert player is not None

        components = separate_crafting_components(player, args[1:])
        if 'error' in components:
            bad_reference = components['error']
            await context.send(f'<@{discord_id}> Invalid reference ID: {bad_reference}')
            return
        
        best_recipe_finder = find_best_recipe(
            goal_item,
            item_index.recipes[goal_item_id],
            player,
            components['ingredients'],
            components['tools'],
            components['handheld']
        )
        if 'error' in best_recipe_finder:
            error_message = best_recipe_finder['error']
            await context.send(f'<@{discord_id} {error_message}')
            return
        
        best_recipe = best_recipe_finder['recipe']
        endurance_cost = best_recipe_finder['cost']

        if endurance_cost > player.endurance:
            if not use_hp:
                message = f'<@{discord_id}> You do not have enough endurance to craft.'
                message += ' Use !craftx instead to use HP.'
                await context.send(message)
                return
            elif endurance_cost > player.endurance + player.hp:
                message = f'<@{discord_id}> You do not have enough endurance/hp to craft.'
                await context.send(message)
                return
        
        best_recipe.apply(player, endurance_cost)
        session.commit()
        await context.send('<@{discord_id}> Successfully crafted {}!')
        await context.send('Lost endurance')
        await context.send('Lost HP')
