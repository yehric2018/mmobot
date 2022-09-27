from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Player
from mmobot.utils.discord import handle_mentions

async def give_logic(bot, context, args, engine):
    if context.channel.name not in bot.zones:
        return
    if len(args) != 2:
        await context.send(f'Please supply give arguments like this: **!give player item**')
        return
    
    giver_name = context.author.nick
    receiver_name = handle_mentions(args[0], context.message.mentions)
    item_name = args[1]
    if all(member.nick != receiver_name for member in context.channel.members):
        await context.send(f'Could not find player {receiver_name} in current location')
        return
    
    with Session(engine) as session:
        giving_player_statement = select(Player).where(Player.name == giver_name)
        receiving_player_statement = select(Player).where(Player.name == receiver_name)
        giving_player = session.scalars(giving_player_statement).one()
        receiving_player = session.scalars(receiving_player_statement).one()

        giving_item = None
        for item in giving_player.inventory:
            if item.id == item_name:
                giving_item = item
                giving_player.inventory.remove(item)
                break
        if giving_item == None:
            if item_name.isnumeric() and int(item_name) < len(giving_player.inventory):
                giving_item = giving_player.inventory[int(item_name)]
            else:
                await context.send(f'You do not have the item: {item_name}')
                return
        receiving_player.inventory.append(giving_item)

        session.commit()
        await context.send(f'<@{receiving_player.discord_id}> received {giving_item.id} from {giver_name}!')