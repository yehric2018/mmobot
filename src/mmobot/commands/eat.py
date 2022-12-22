from sqlalchemy.orm import Session

from mmobot.db.models import Player, SolidFood
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id
from mmobot.utils.players import find_item_with_id, find_item_with_name


async def eat_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) != 1:
        message = 'Please indicate what item you would like to eat, for example: !eat food'
        await context.send(message)
        return

    item_reference = args[0]
    discord_id = context.author.id
    with Session(engine) as session:
        player = Player.select_with_discord_id(session, discord_id)
        assert player is not None
        if player.stats.hp == 0:
            message = f'<@{player.discord_id}> You are incapacitated.'
            await context.send(message)
            return

        if is_entity_id(item_reference):
            item_id = convert_alphanum_to_int(item_reference)
            eat_item = find_item_with_id(player.inventory, item_id)
        else:
            eat_item = find_item_with_name(player.inventory, item_reference)
        if not eat_item:
            message = f'<@{player.discord_id}> Could not find item to eat: {item_reference}'
            await context.send(message)
            return

        ate_food_message = f'<@{player.discord_id}> ate {eat_item.item_id}'
        if isinstance(eat_item.item, SolidFood):
            await context.send(ate_food_message)
            await eat_solid_food(context, session, player, eat_item)
            session.commit()
        else:
            await context.send(f'<@{player.discord_id}> You cannot eat {eat_item.item_id}!')


async def eat_solid_food(context, session, player, food_instance):
    food_item = food_instance.item
    player.stats.hp += food_item.hp_recover
    player.stats.endurance += food_item.endurance_recover
    if food_item.hp_recover > 0:
        await context.send(f'Recovered {food_item.hp_recover} HP')
    elif food_item.hp_recover < 0:
        await context.send(f'Lost {-food_item.hp_recover} HP')
    if food_item.endurance_recover > 0:
        await context.send(f'Recovered {food_item.endurance_recover} endurance')
    elif food_item.endurance_recover < 0:
        await context.send(f'Lost {-food_item.endurance_recover} endurance')
    session.delete(food_instance)
