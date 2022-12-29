import os
import sys
import yaml

import discord
from discord import Intents, PermissionOverwrite
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from mmobot.db.models import Zone
from mmobot.db import initialize_engine


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

engine = initialize_engine()

grid = [
    [0, 1, 0],
    [2, 3, 4],
    [0, 5, 0]
]


def get_zones():
    with open('src/mmobot/db/zone-channels.yaml', 'r') as f:
        try:
            zones_list = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(exc)
    return zones_list


async def add_general_channel(guild, channel_name):
    channel = discord.utils.get(guild.channels, name=channel_name)
    if channel is None:
        print(f'Creating general channel #{channel_name}...')
        channel = await guild.create_text_channel(channel_name)
        print('\tChannel created!')
    else:
        print(f'General channel #{channel_name} already exists')
    return channel


async def add_zones(guild):
    overwrites = {
        guild.default_role: PermissionOverwrite(read_messages=False),
        guild.me: PermissionOverwrite(read_messages=True)
    }
    world_category = discord.utils.get(guild.categories, name='World')
    if world_category is None:
        world_category = await guild.create_category('World')
    zones = get_zones()

    with Session(engine) as session:
        for index, zone_name in enumerate(zones):
            channel = discord.utils.get(guild.channels, name=zone_name)
            if channel is None:
                print(f'Creating zone channel #{zone_name}...')
                channel = await guild.create_text_channel(
                    zone_name,
                    overwrites=overwrites,
                    category=world_category
                )
                new_zone = Zone(
                    id=index,
                    channel_id=channel.id,
                    channel_name=channel.name
                )
                session.add(new_zone)
                print('\tChannel created!')
            else:
                print(f'Zone channel #{zone_name} already exists')
        session.commit()


async def setup_server(guild):
    await add_general_channel(guild, 'general')
    await add_general_channel(guild, 'new-players')

    await add_zones(guild)


if len(sys.argv) < 2:
    print('Usage: python setup_server.py [GUILD ID]')
    quit()
if not sys.argv[1].isnumeric():
    print('ERROR: Please enter a valid server/guild id')
    quit()

guild_id = int(sys.argv[1])

intents = Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    guild = client.get_guild(guild_id)
    if guild is None:
        print(f'Guild/server {guild_id} does not exist for this bot')
        await client.close()
        print('Client closed')
        return
    await setup_server(guild)
    print('Server set up successfully. You may now close the client.')


client.run(TOKEN)
