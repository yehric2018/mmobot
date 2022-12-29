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

    giving_item_name = args[1]
    with Session(engine) as session:
        giving_player = Player.select_with_discord_id(session, context.author.id)
        assert giving_player is not None
        if giving_player.hp == 0:
            message = f'<@{giving_player.discord_id}> You are incapacitated.'
            await context.send(message)
            return

        if is_mention(args[0]):
            receiving_player = Player.select_with_discord_id(
                session, args[0][2:-1], channel_id=context.channel.id
            )
        else:
            receiving_player = Player.select_with_discord_name(
                session, args[0], channel_id=context.channel.id
            )
        if receiving_player is None:
            await context.send(f'Could not find player {args[0]} in current location')
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
        if giving_player.equipped_weapon_id == giving_item_instance.id:
            giving_player.equipped_weapon_id = None
        giving_item_instance.owner_id = receiving_player.id
        session.commit()

        message = '<@{0}> received {1} from {2}!'.format(
            receiving_player.discord_id,
            giving_item_instance.item.id,
            context.author.nick
        )
        await context.send(message)
