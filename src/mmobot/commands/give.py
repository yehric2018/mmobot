from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Player
from mmobot.utils.discord import is_mention
from mmobot.utils.entities import convert_alphanum_to_int
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
        receiving_player_statement = select(Player).where(Player.discord_id == receiver_id)
        if all(member.id != receiver_id for member in context.channel.members):
            await context.send(f'Could not find player {args[0]} in current location')
            return
    else:
        receiver_name = args[0]
        receiving_player_statement = select(Player).where(Player.name == receiver_name)
        if all(member.nick != receiver_name for member in context.channel.members):
            await context.send(f'Could not find player {args[0]} in current location')
            return

    with Session(engine) as session:
        giving_player_statement = select(Player).where(Player.name == giver_name)
        giving_player = session.scalars(giving_player_statement).one()
        receiving_player = session.scalars(receiving_player_statement).one()

        giving_item_instance = None

        if giving_item_name.startswith('/'):
            giving_item_id = convert_alphanum_to_int(giving_item_name[1:])
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
