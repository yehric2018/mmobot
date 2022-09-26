from datetime import datetime
import os

import discord

from discord import DiscordException, Embed
from dotenv import load_dotenv
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from MMOBot import MMOBot
from constants import STANCE_NORMAL
from db.models import Player, Weapon
from utils.discord import handle_mentions
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

@bot.command(name='give')
async def give_command(context, *args):
    if context.channel.name not in bot.zones:
        return
    if len(args) != 2:
        await context.send(f'Please supply give arguments like this: **!give player item**')
        return
    
    giver_name = context.author.nick
    receiver_name = handle_mentions(args[0], context.message.mentions)
    item_name = args[1]
    if all(member.nick != receiver_name for member in context.channel.members):
        await context.send(f'Could not find player {receiver_name} in current location')
        return
    
    with Session(engine) as session:
        giving_player_statement = select(Player).where(Player.name == giver_name)
        receiving_player_statement = select(Player).where(Player.name == receiver_name)
        giving_player = session.scalars(giving_player_statement).one()
        receiving_player = session.scalars(receiving_player_statement).one()

        giving_item = None
        for item in giving_player.inventory:
            if item.name == item_name:
                giving_item = item
                giving_player.inventory.remove(item)
                break
        if giving_item == None:
            if item_name.isnumeric() and int(item_name) < len(giving_player.inventory):
                giving_item = giving_player.inventory[int(item_name)]
            else:
                await context.send(f'You do not have the item: {item_name}')
                return
        receiving_player.inventory.append(giving_item)

        session.commit()
        await context.send(f'<@{receiving_player.discord_id}> received {giving_item.name} from {giver_name}!')

@bot.command(name='inventory')
async def inventory_command(context):
    with Session(engine) as session:
        get_player_statement = (select(Player)
            .where(Player.discord_id == context.author.id)
            .where(Player.is_active))
        try:
            player = session.scalars(get_player_statement).one()
            message = ''
            for index, item in enumerate(player.inventory):
                message += f'  {index}. {item.name}'
                if (item.id == player.equipped_weapon or
                        item.id == player.equipped_attire or
                        item.id == player.equipped_accessory):
                    message += '(equipped)'
                message += '\n'
            embed = Embed(
                title=f'{context.author.nick}\'s Inventory',
                description=message
            )
            await context.send(embed=embed)
        except NoResultFound:
            raise DiscordException

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
    if len(args) > 1:
        await context.send(f'Your name can only be one word, sorry!')
        return

    player_name = args[0]
    if len(player_name) < 2 or len(player_name) > 20:
        await context.send(f'Your name must be between 2 and 20 characters')
        return

    with Session(engine) as session:
        stats = roll_initial_stats()
        get_ancestors_statement = (select(func.max(Player.ancestry))
                .where(Player.discord_id == context.author.id))
        max_ancestry = session.scalars(get_ancestors_statement).one()
        if max_ancestry == None:
            max_ancestry = 0
        else:
            max_ancestry = int(max_ancestry)
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
            magic_number=0,
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