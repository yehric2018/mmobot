from discord import Embed
from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Zone
from mmobot.utils.entities import convert_int_to_alphanum


async def here_logic(context, engine):
    if context.channel.category.name != 'World':
        return

    with Session(engine) as session:
        get_zone_statement = (
            select(Zone)
            .where(Zone.channel_name == context.channel.name)
        )
        zone = session.scalars(get_zone_statement).one()
        embed = Embed(
            title=f'You are at: {context.channel.name}:'
        )
        navigation_message = ''
        for zone_path in zone.navigation:
            navigation_message += f' > {zone_path.end_zone_name}\n'
        interactions_message = ''
        for interaction in zone.interactions:
            interaction_id = f'/{convert_int_to_alphanum(interaction.id)}'
            interactions_message += f'> [ {interaction_id} ] {interaction.title}\n'
        loot_message = ''
        for item_instance in zone.loot:
            item_instance_id = f'/{convert_int_to_alphanum(item_instance.id)}'
            item_name = item_instance.item.id
            loot_message += f'> [ {item_instance_id} ] {item_name}\n'
        if len(navigation_message) == 0:
            navigation_message = '> No places to travel.'
        if len(interactions_message) == 0:
            interactions_message = '> Nothing to interact with.'
        if len(loot_message) == 0:
            loot_message = '> No items to pick up.'
        embed.add_field(name='Navigation', value=navigation_message)
        embed.add_field(name='Interactions', value=interactions_message)
        embed.add_field(name='Loot', value=loot_message)
        await context.send(embed=embed)
