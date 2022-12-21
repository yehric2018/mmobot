from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Player
from mmobot.utils.discord import is_mention
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id
from mmobot.utils.players import find_item_with_id, find_item_with_name


async def give_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) != 2:
        await context.send('Please supply give arguments like this: **!give player item**')
        return

    giver_name = context.author.nick
    giving_item_name = args[1]

    if is_mention(args[0]):
        receiver_id = int(args[0][2:-1])
        receiving_player_statement = (
            select(Player)
            .where(Player.discord_id == receiver_id)
            .where(Player.is_active)
            .where(Player.zone == context.channel.name)
        )
    else:
        receiver_name = args[0]
        receiving_player_statement = (
            select(Player)
            .where(Player.name == receiver_name)
            .where(Player.is_active)
            .where(Player.zone == context.channel.name)
        )

    with Session(engine) as session:
        receiving_player = session.scalars(receiving_player_statement).one_or_none()
        if receiving_player is None:
            await context.send(f'Could not find player {args[0]} in current location')
            return
        giving_player_statement = select(Player).where(Player.name == giver_name)
        giving_player = session.scalars(giving_player_statement).one()
        if giving_player.stats.hp == 0:
            message = f'<@{giving_player.discord_id}> You are incapacitated.'
            await context.send(message)
            return

        giving_item_instance = None

        if is_entity_id(giving_item_name):
            giving_item_id = convert_alphanum_to_int(giving_item_name)
            giving_item_instance = find_item_with_id(giving_player.inventory, giving_item_id)
        elif (giving_item_name.isnumeric() and
                int(giving_item_name) < len(giving_player.inventory)):
            giving_item_instance = giving_player.inventory[int(giving_item_name)]
        else:
            giving_item_instance = find_item_with_name(giving_player.inventory, giving_item_name)

        if giving_item_instance is None:
            await context.send(f'You do not have the item: {giving_item_name}')
            return
        giving_item_instance.player_id = receiving_player.id
        if giving_player.equipped_weapon_id == giving_item_instance.id:
            giving_player.equipped_weapon_id = None
        session.commit()

        message = '<@{0}> received {1} from {2}!'.format(
            receiving_player.discord_id,
            giving_item_instance.item.id,
            giver_name
        )
        await context.send(message)
