from discord import Embed
from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Zone


async def navigation_logic(context, engine):
    if context.channel.category.name != 'World':
        return

    with Session(engine) as session:
        zone = Zone.select_with_channel_id(session, context.channel.id)
        assert zone is not None

        embed = Embed(
            title=f'You can reach the following locations from {context.channel.name}:'
        )

        if zone.can_move_west():
            embed.add_field(
                name=':arrow_left: West',
                value=zone.west_zone.channel_name,
                inline=True
            )
        if zone.can_move_north():
            embed.add_field(
                name=':arrow_up: North',
                value=zone.north_zone.channel_name,
                inline=True
            )
        if zone.can_move_south():
            embed.add_field(
                name=':arrow_down: South',
                value=zone.south_zone.channel_name,
                inline=True
            )
        if zone.can_move_east():
            embed.add_field(
                name=':arrow_right: East',
                value=zone.east_zone.channel_name,
                inline=True
            )

        await context.send(embed=embed)
