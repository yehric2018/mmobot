import discord
from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Player, Zone


async def move_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) == 0:
        await context.send('Please specify a location to move to! For example: !move hawaii')
        return

    zone_name = args[0]
    member = context.author
    curr_channel = context.channel
    with Session(engine) as session:
        get_player_statement = (
            select(Player)
            .where(Player.discord_id == context.author.id)
            .where(Player.is_active)
        )
        player = session.scalars(get_player_statement).one()
        if player.hp == 0:
            message = f'<@{player.discord_id}> You are incapacitated.'
            await context.send(message)
            return

        get_zone_statement = (
            select(Zone)
            .where(Zone.channel_name == context.channel.name)
        )
        zone = session.scalars(get_zone_statement).one()
        if zone.minizone_parent == zone_name:
            dest_channel = discord.utils.get(context.guild.channels, name=zone_name)
            player.zone = zone_name
            session.commit()

            await curr_channel.send(f'{member.mention} has left.')

            await dest_channel.set_permissions(member, read_messages=True, send_messages=True)
            await curr_channel.remove_user(member)
        elif any(zone_path.end_zone_name == zone_name for zone_path in zone.navigation):
            dest_channel = discord.utils.get(context.guild.channels, name=zone_name)
            player.zone = zone_name
            session.commit()

            await curr_channel.send(f'{member.mention} has left for {dest_channel.mention}.')

            await dest_channel.set_permissions(member, read_messages=True, send_messages=True)
            await curr_channel.set_permissions(member, read_messages=False, send_messages=False)

            await dest_channel.send(f'{member.mention} has arrived.')
        elif any(minizone.channel_name == zone_name for minizone in zone.minizones):
            dest_thread = discord.utils.get(curr_channel.threads, name=zone_name)
            player.zone = zone_name
            session.commit()

            await curr_channel.send(f'{member.mention} has entered {dest_thread.mention}.')

            await dest_thread.add_user(member)
            await curr_channel.set_permissions(member, read_messages=True, send_messages=False)

            await dest_thread.send(f'{member.mention} has arrived.')
        else:
            await context.send(f'You cannot travel to {zone_name} from {context.channel.name}')
