import os

import discord

from discord.ext import tasks
from dotenv import load_dotenv

from mmobot.db import initialize_engine
from mmobot.jobs.cron import (
    decrement_hp,
    increment_skill_points
)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)


engine = initialize_engine()


@client.event
async def on_ready():
    all_tasks = []
    all_tasks.append(decrement_hp_task.start())
    all_tasks.append(increment_skill_points_task.start())
    print(f'{client.user.name} has connected to Discord!')


@tasks.loop(hours=2)
async def decrement_hp_task():
    if decrement_hp_task.current_loop != 0:
        await decrement_hp(client, engine)


@tasks.loop(hours=12)
async def increment_skill_points_task():
    if increment_skill_points_task.current_loop != 0:
        await increment_skill_points(engine)


client.run(TOKEN)
