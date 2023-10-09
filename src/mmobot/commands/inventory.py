from discord import Embed
from sqlalchemy.orm import Session

from mmobot.db.models import Player
from mmobot.utils.entities import convert_int_to_alphanum


async def inventory_logic(context, engine):
    if context.channel.category.name != 'World':
        return

    with Session(engine) as session:
        player = Player.select_with_discord_id(session, context.author.id)
        assert player is not None
        message = ''
        for index, item_instance in enumerate(player.inventory):
            display_id = convert_int_to_alphanum(item_instance.id)
            message += f'  {index}. [ /{display_id} ] : {item_instance.item.id}'
            if player.equipped_weapon_id == item_instance.id:
                message += ' **(weapon)**'
            message += '\n'
        embed = Embed(
            title=f'{context.author.nick}\'s Inventory',
            description=message
        )
        await context.send(embed=embed)
