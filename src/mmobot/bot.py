import os

import discord

from dotenv import load_dotenv
from sqlalchemy import create_engine

from MMOBot import MMOBot
from commands import give_logic, inventory_logic, move_logic, name_logic, navigation_logic

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_DATABASE_NAME = os.getenv('MYSQL_DATABASE_NAME')

connection_str = f'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
    MYSQL_USERNAME,
    MYSQL_PASSWORD,
    MYSQL_HOSTNAME,
    MYSQL_DATABASE_NAME
)

engine = create_engine()
bot = MMOBot()


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
async def attack_command(context):
    await context.send('You cannot attack yet')


@bot.command(name='give')
async def give_command(context, *args):
    await give_logic(bot, context, args, engine)


@bot.command(name='inventory')
async def inventory_command(context):
    await inventory_logic(context, engine)


@bot.command(name='me')
async def me_command(context):
    await context.send(f'Your name is {context.author.nick}')


@bot.command(name='move')
async def move_command(context, *args):
    await move_logic(bot, context, args)


@bot.command(name='navigation')
async def navigation_command(context):
    await navigation_logic(bot, context)


@bot.command(name='name')
async def name_command(context, *args):
    await name_logic(context, args, engine)


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')

bot.run(TOKEN)
