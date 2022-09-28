from discord import Embed
from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Zone


async def navigation_logic(bot, context, engine):
    if context.channel.name not in bot.zones:
        return

    with Session(engine) as session:
        get_zone_statement = (
            select(Zone)
            .where(Zone.channel_name == context.channel.name)
        )
        zone = session.scalars(get_zone_statement).one()
        message = ''
        for index, zone_path in enumerate(zone.navigation):
            message += f'{index}. {zone_path.end_zone_name}\n'
        embed = Embed(
            title=f'You can reach the following locations from {context.channel.name}:',
            description=message
        )
        await context.send(embed=embed)
