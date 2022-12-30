from sqlalchemy.orm import Session

from mmobot.db.models import FluidContainerInstance, FluidFood, Player, SolidFood
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id
from mmobot.utils.players import find_item_with_id, find_item_with_name


async def eat_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) < 1:
        message = 'Please indicate what item you would like to eat, for example: !eat food'
        await context.send(message)
        return

    item_reference = args[0]
    discord_id = context.author.id
    with Session(engine) as session:
        player = Player.select_with_discord_id(session, discord_id)
        assert player is not None
        if player.hp == 0:
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

        if isinstance(eat_item.item, SolidFood):
            await eat_solid_food(context, session, player, eat_item)
            player.inventory_weight -= eat_item.item.weight
            session.commit()
        elif isinstance(eat_item, FluidContainerInstance):
            if len(args) >= 2 and args[1].isnumeric() and int(args[1]) > 0:
                await eat_from_container(context, player, eat_item, units=int(args[1]))
            else:
                await eat_from_container(context, player, eat_item)
            session.commit()
        else:
            await context.send(f'<@{player.discord_id}> You cannot eat {eat_item.item_id}!')


async def eat_solid_food(context, session, player, food_instance):
    await context.send(f'<@{player.discord_id}> ate {food_instance.item_id}')
    food_item = food_instance.item
    hp_recover = min(player.max_hp - player.hp, food_item.hp_recover)
    endurance_recover = min(
        player.max_endurance - player.endurance,
        food_item.endurance_recover
    )

    player.hp += hp_recover
    player.endurance += endurance_recover

    if hp_recover > 0:
        await context.send(f'Recovered {hp_recover} HP')
    elif hp_recover < 0:
        await context.send(f'Lost {- hp_recover} HP')
    if endurance_recover > 0:
        await context.send(f'Recovered {endurance_recover} endurance')
    elif endurance_recover < 0:
        await context.send(f'Lost {- endurance_recover} endurance')
    session.delete(food_instance)


async def eat_from_container(context, player, container_instance, units=1):
    if container_instance.nonsolid_id is None:
        await context.send(f'<@{player.discord_id}> {container_instance.id} is empty')
        return
    elif not isinstance(container_instance.nonsolid, FluidFood):
        message = f'<@{player.discord_id}> You cannot eat {container_instance.nonsolid_id}'
        await context.send(message)
        return

    assert units > 0
    await context.send(f'<@{player.discord_id}> ate {container_instance.nonsolid_id}')
    food = container_instance.nonsolid
    units = min(units, container_instance.units)
    hp_recover = min(player.max_hp - player.hp, units * food.hp_recover)
    endurance_recover = min(
        player.max_endurance - player.endurance,
        units * food.endurance_recover
    )

    player.hp += hp_recover
    player.endurance += endurance_recover

    if hp_recover > 0:
        await context.send(f'Recovered {hp_recover} HP')
    elif hp_recover < 0:
        await context.send(f'Lost {- hp_recover} HP')
    if endurance_recover > 0:
        await context.send(f'Recovered {endurance_recover} endurance')
    elif endurance_recover < 0:
        await context.send(f'Lost {- endurance_recover} endurance')
    container_instance.units -= units
    if container_instance.units == 0:
        container_instance.nonsolid_id = None
