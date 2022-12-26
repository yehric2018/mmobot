from sqlalchemy.orm import Session

from mmobot.db.models import Player, Zone
from mmobot.utils.crafting import find_best_recipe, separate_crafting_components


async def craft_logic(context, args, engine, item_index, use_hp=False):
    if context.channel.category.name != 'World':
        return
    if len(args) == 0:
        message = f'<@{context.author.id}> Please supply craft arguments like this: '
        message += '**!craft item ingredient1 ingredient2 ...**'
        await context.send(message)
        return

    goal_item_id = args[0]
    discord_id = context.author.id
    if goal_item_id not in item_index.index:
        await context.send(f'<@{discord_id}> {goal_item_id} does not exist.')
        return
    elif len(item_index.recipes[goal_item_id]) == 0:
        await context.send(f'<@{discord_id}> You cannot craft {goal_item_id}.')
        return

    goal_item = item_index.index[goal_item_id]
    with Session(engine) as session:
        player = Player.select_with_discord_id(session, discord_id)
        assert player is not None
        zone = Zone.select_with_channel_name(session, player.zone)
        assert zone is not None

        components = separate_crafting_components(args[1:], player, zone)
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

        if endurance_cost > player.stats.endurance:
            if not use_hp:
                message = f'<@{discord_id}> You do not have enough endurance to craft.'
                message += ' Use !craftx instead to use HP.'
                await context.send(message)
                return
            elif endurance_cost > player.stats.endurance + player.stats.hp:
                message = f'<@{discord_id}> You do not have enough endurance/hp to craft.'
                await context.send(message)
                return

        initial_endurance = player.stats.endurance
        initial_hp = player.stats.hp
        best_recipe.apply(
            player,
            endurance_cost,
            ingredients=components['ingredients'],
            tools=components['tools'],
            handheld=components['handheld']
        )
        session.commit()
        await context.send(f'<@{discord_id}> Successfully crafted {goal_item_id}!')
        if player.stats.endurance < initial_endurance:
            await context.send(f'Lost {initial_endurance - player.stats.endurance} endurance')
        if player.stats.hp < initial_hp:
            await context.send(f'Lost {initial_hp - player.stats.hp} HP')
