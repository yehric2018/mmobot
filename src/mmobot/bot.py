import os

import discord

from discord import DiscordException
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from MMOBot import MMOBot
from commands import give_logic, inventory_logic, move_logic, name_logic, navigation_logic
from db.models import Player

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_DATABASE_NAME = os.getenv('MYSQL_DATABASE_NAME')

engine = create_engine(f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}/{MYSQL_DATABASE_NAME}')
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
    with Session(engine) as session:
        get_player_statement = (select(Player)
            .where(Player.discord_id == context.author.id)
            .where(Player.is_active))
        try:
            player = session.scalars(get_player_statement).one()
        except NoResultFound:
            raise DiscordException

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
        else:
            raise

bot.run(TOKEN)