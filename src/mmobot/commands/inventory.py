from discord import DiscordException, Embed
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from mmobot.db.models import Player

async def inventory_logic(context, engine):
    with Session(engine) as session:
        get_player_statement = (select(Player)
            .where(Player.discord_id == context.author.id)
            .where(Player.is_active))
        try:
            player = session.scalars(get_player_statement).one()
            message = ''
            for index, item in enumerate(player.inventory):
                message += f'  {index}. {item.id}'
                if (item.id == player.equipped_weapon or
                        item.id == player.equipped_attire or
                        item.id == player.equipped_accessory):
                    message += '(equipped)'
                message += '\n'
            embed = Embed(
                title=f'{context.author.nick}\'s Inventory',
                description=message
            )
            await context.send(embed=embed)
        except NoResultFound:
            raise DiscordException