import discord
from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Zone


async def move_logic(zones, context, args, engine):
    member = context.author
    if context.channel.name not in zones:
        return
    if len(args) == 0:
        await context.send('Please specify a location to move to! For example: !move hawaii')
        return

    zone_name = args[0]
    if zone_name not in zones:
        await context.send(f'{zone_name} is not an existing location')
        return

    with Session(engine) as session:
        get_zone_statement = (
            select(Zone)
            .where(Zone.channel_name == context.channel.name)
        )
        zone = session.scalars(get_zone_statement).one()
        if all(zone_path.end_zone_name != zone_name for zone_path in zone.navigation):
            await context.send(f'You cannot travel to {zone_name} from {context.channel.name}')
            return
        curr_channel = discord.utils.get(context.guild.channels, name=context.channel.name)
        dest_channel = discord.utils.get(context.guild.channels, name=zone_name)

        await curr_channel.send(f'{member.mention} has left for {dest_channel.mention}.')

        await dest_channel.set_permissions(member, read_messages=True, send_messages=True)
        await curr_channel.set_permissions(member, read_messages=False, send_messages=False)

        await dest_channel.send(f'{member.mention} has arrived.')
