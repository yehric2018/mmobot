from discord import Embed
from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Zone
from mmobot.utils.entities import convert_int_to_alphanum


async def here_logic(context, engine):
    if context.channel.category.name != 'World':
        return

    with Session(engine) as session:
        zone = Zone.select_with_channel_id(session, context.channel.id)
        assert zone is not None
        embed = Embed(
            title=f'You are at: {context.channel.name}:'
        )
        interactions_message = ''
        for interaction in zone.interactions:
            interaction_id = f'/{convert_int_to_alphanum(interaction.id)}'
            interactions_message += f'> [ {interaction_id} ] {interaction.title}\n'
        monsters_message = ''
        for monster in zone.monsters:
            monsters_message += f'> {monster.get_name()}'
        loot_message = ''
        for item_instance in zone.loot:
            item_instance_id = f'/{convert_int_to_alphanum(item_instance.id)}'
            item_name = item_instance.item.id
            loot_message += f'> [ {item_instance_id} ] {item_name}\n'
        if len(monsters_message) == 0:
            monsters_message = '> No monsters here.'
        if len(interactions_message) == 0:
            interactions_message = '> Nothing to interact with.'
        if len(loot_message) == 0:
            loot_message = '> No items to pick up.'
        embed.add_field(name='Monsters', value=monsters_message)
        embed.add_field(name='Interactions', value=interactions_message)
        embed.add_field(name='Loot', value=loot_message)
        await context.send(embed=embed)
