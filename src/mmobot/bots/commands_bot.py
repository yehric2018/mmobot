import os

import discord

from discord.ext import commands
from dotenv import load_dotenv

from mmobot.commands import (
    attack_logic,
    drop_logic,
    eat_logic,
    equip_logic,
    give_logic,
    here_logic,
    inventory_logic,
    learn_logic,
    move_logic,
    name_logic,
    navigation_logic,
    pickup_logic,
    teach_logic,
    unequip_logic,
)
from mmobot.db import initialize_engine

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


engine = initialize_engine()


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Greetings @{member.name}, welcome to the world of Dishord!'
    )
    start_channel = discord.utils.get(member.guild.channels, name='new-players')
    await start_channel.set_permissions(member, read_messages=True, send_messages=True)


@bot.command(name='attack')
async def attack_command(context, *args):
    await attack_logic(bot, context, args, engine)


@bot.command(name='drop')
async def drop_command(context, *args):
    await drop_logic(context, args, engine)


@bot.command(name='eat')
async def eat_command(context, *args):
    await eat_logic(context, args, engine)


@bot.command(name='equip')
async def equip_command(context, *args):
    await equip_logic(context, args, engine)


@bot.command(name='give')
async def give_command(context, *args):
    await give_logic(context, args, engine)


@bot.command(name='here')
async def here_command(context):
    await here_logic(context, engine)


@bot.command(name='inventory')
async def inventory_command(context):
    await inventory_logic(context, engine)


@bot.command(name='learn')
async def learn_command(context, *args):
    await learn_logic(context, args, engine)


@bot.command(name='me')
async def me_command(context):
    await context.send(f'Your name is {context.author.nick}')


@bot.command(name='move')
async def move_command(context, *args):
    await move_logic(context, args, engine)


@bot.command(name='navigation')
async def navigation_command(context):
    await navigation_logic(context, engine)


@bot.command(name='name')
async def name_command(context, *args):
    await name_logic(context, args, engine)


@bot.command(name='pickup')
async def pickup_command(context, *args):
    await pickup_logic(context, args, engine)


@bot.command(name='teach')
async def teach_command(context, *args):
    await teach_logic(context, args, engine)


@bot.command(name='unequip')
async def unequip_command(context, *args):
    await unequip_logic(context, args, engine)


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')


bot.run(TOKEN)
