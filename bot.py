import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Greetings @{member.name}, welcome to the world of Lazuranth!'
    )
    print(f'Sent welcome message to {bot.user.name}')

@bot.command(name='attack')
async def attack_command(context):
    await context.send('You cannot attack yet')

@bot.command(name='me')
async def me_command(context):
    await context.send(f'Your name is {context.author.nick}')

@bot.command(name='move')
async def move_command(context, *args):
    if len(args) == 0:
        await context.send(f'Please specify a location to move to! For example: !move hawaii')
        return

    zone_name = args[0]
    member = context.author
    curr_channel = discord.utils.get(context.guild.channels, name=context.channel.name)
    dest_channel = discord.utils.get(context.guild.channels, name=zone_name)
    
    if curr_channel.name not in ['general', 'dev'] and not member.guild_permissions.administrator:
        await dest_channel.set_permissions(member, read_messages=True, send_messages=True)
        await curr_channel.set_permissions(member, read_messages=False, send_messages=False)

@bot.command(name='name')
async def name_command(context, *args):
    if len(args) == 0:
        await context.send(f'Please enter the name of your hero! For example: !name Joanne')
    
    player_name = args[0]
    member = context.author
    if context.channel.name == 'new-players':
        await member.edit(nick=player_name)
    else:
        await context.send('Invalid command')

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)