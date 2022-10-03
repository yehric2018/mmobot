from discord import DiscordException, Embed
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from mmobot.db.models import Player
from mmobot.utils.entities import convert_int_to_alphanum


async def inventory_logic(zones, context, engine):
    if context.channel.name not in zones:
        return

    with Session(engine) as session:
        get_player_statement = (
            select(Player)
            .where(Player.discord_id == context.author.id)
            .where(Player.is_active)
        )
        try:
            player = session.scalars(get_player_statement).one()
            message = ''
            for index, item_instance in enumerate(player.inventory):
                display_id = convert_int_to_alphanum(item_instance.id)
                message += f'  {index}. [ /{display_id} ] : {item_instance.item.id}'
                message += '\n'
            embed = Embed(
                title=f'{context.author.nick}\'s Inventory',
                description=message
            )
            await context.send(embed=embed)
        except NoResultFound:
            raise DiscordException
