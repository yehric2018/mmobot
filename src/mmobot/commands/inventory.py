from discord import Embed
from sqlalchemy.orm import Session

from mmobot.db.models import FluidContainerInstance, Player
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
            if isinstance(item_instance, FluidContainerInstance):
                if item_instance.units == 0:
                    message += ' (empty)'
                else:
                    fill_ratio = f'{item_instance.units}/{item_instance.item.max_capacity}'
                    message += f' ({item_instance.nonsolid_id} {fill_ratio})'
            if player.equipped_weapon_id == item_instance.id:
                message += ' **(weapon)**'
            message += '\n'
        embed = Embed(
            title=f'{context.author.nick}\'s Inventory',
            description=message
        )
        await context.send(embed=embed)
