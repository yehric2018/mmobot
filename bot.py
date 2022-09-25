from datetime import datetime
import os

import discord
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from MMOBot import MMOBot
from constants import STANCE_NORMAL
from db.models import Player
from utils.stats import roll_initial_stats

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

@bot.command(name='me')
async def me_command(context):
    await context.send(f'Your name is {context.author.nick}')

@bot.command(name='move')
async def move_command(context, *args):
    if context.channel.name not in bot.zones:
        return
    if len(args) == 0:
        await context.send(f'Please specify a location to move to! For example: !move hawaii')
        return

    zone_name = args[0]
    if zone_name not in bot.zones:
        await context.send(f'{zone_name} is not an existing location')
        return
    if zone_name not in bot.zones[context.channel.name].navigation:
        await context.send(f'You cannot travel to {zone_name} from {context.channel.name}')
        return
    member = context.author
    curr_channel = discord.utils.get(context.guild.channels, name=context.channel.name)
    dest_channel = discord.utils.get(context.guild.channels, name=zone_name)
    
    if curr_channel.name not in ['general', 'dev'] and not member.guild_permissions.administrator:
        await dest_channel.set_permissions(member, read_messages=True, send_messages=True)
        await curr_channel.set_permissions(member, read_messages=False, send_messages=False)

@bot.command(name='navigation')
async def navigation_command(context):
    if context.channel.name not in bot.zones:
        return
    
    message = f'You can reach the following locations from {context.channel.name}:\n'
    for location in bot.zones[context.channel.name].navigation:
        zone_props = bot.zones[context.channel.name].navigation[location]
        message += f'    {location}'
        if zone_props['lockable'] and zone_props['locked']:
            message += ' (locked)'
        if zone_props['guardable'] and len(zone_props['guards']) > 0:
            guard_list = ', '.join(zone_props['guards'])
            message += f' (guarded by {guard_list})'
        message += '\n'
    
    await context.send(message, ephemeral=True)

@bot.command(name='name')
async def name_command(context, *args):
    if context.channel.name != 'new-players':
        return
    if len(args) == 0:
        await context.send(f'Please enter the name of your hero! For example: !name Joanne')
        return
    
    for word in args:
        if not word.isalnum():
            await context.send(f'Your name can only include alphanumeric characters')
            return
    player_name = ' '.join(args)
    if len(player_name) < 2 or len(player_name) > 20:
        await context.send(f'Your name must be between 2 and 20 characters')
        return

    with Session(engine) as session:
        stats = roll_initial_stats()
        get_ancestors_statement = select(Player).where(Player.discord_id == context.author.id)
        max_ancestry = 0
        for ancestor in session.scalars(get_ancestors_statement):
            if ancestor.is_active:
                message = f'Cannot start new player - {ancestor.name} is still fighting hard and strong!'
                await context.send(message)
                return
            if ancestor.ancestry > max_ancestry:
                max_ancestry = ancestor.ancestry
        birthday = datetime.now()
        new_player = Player(
            name=player_name,
            discord_id=f'{context.author.id}',
            ancestry=max_ancestry + 1,
            birthday=birthday,
            is_active=True,
            stance=STANCE_NORMAL,
            hp=stats['hp'],
            max_hp=stats['hp'],
            armor=stats['armor'],
            mobility=stats['mobility'],
            dexterity=stats['dexterity'],
            endurance=stats['endurance'],
            max_endurance=stats['endurance'],
            strength=stats['strength'],
            luck=stats['luck'],
            experience=0,
            magic_number=0,
            fighting_skill=0,
            hunting_skill=0,
            mining_skill=0,
            cooking_skill=0,
            crafting_skill=0
        )

        try:
            session.add(new_player)
            session.commit()
        except IntegrityError:
            await context.send(f'Name {player_name} has already been taken')
            return

        member = context.author
        await member.edit(nick=player_name)

        town_square_channel = discord.utils.get(context.guild.channels, name='town-square')
        await town_square_channel.set_permissions(member, read_messages=True, send_messages=True)

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)