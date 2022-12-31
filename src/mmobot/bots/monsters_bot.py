import os
import discord
import threading

from discord.ext import commands, tasks
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from mmobot.db import initialize_engine
from mmobot.db.index import MonsterIndex
from mmobot.db.models import Entity, MonsterInstance, Player
from mmobot.utils.battle import attack_in_channel
from mmobot.utils.players import handle_incapacitation


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

engine = initialize_engine()
monster_index = MonsterIndex()

active_monsters = {}
lock = threading.Lock()


@bot.event
async def on_ready():
    all_tasks = []
    all_tasks.append(attack_players.start())
    print(f'{bot.user.name} has connected to Discord!')


@tasks.loop(seconds=2)
async def attack_players():
    global active_monsters
    lock.acquire()
    try:
        new_active_monsters = {}
        for instance_id in active_monsters:
            instance = active_monsters[instance_id]
            if instance['loop_offset'] == -1:
                instance['loop_offset'] = attack_players.current_loop
            loop_number = attack_players.current_loop - instance['loop_offset']
            if loop_number % instance['data'].loop_cooldown != 0:
                continue
            with Session(engine) as session:
                monster = MonsterInstance.select_with_reference(session, instance_id)
                if monster is None:
                    continue
                player = Player.select_with_discord_id(session, instance['aggros'][0])
                if player.zone.channel_id == monster.zone.channel_id:
                    channel = await bot.fetch_channel(player.zone.channel_id)
                    await attack_in_channel(channel, monster, player)
                    session.commit()
                    await handle_incapacitation(player, engine, bot)
                    new_active_monsters[instance_id] = instance
        active_monsters = new_active_monsters
    finally:
        lock.release()


@tasks.loop(minutes=1)
async def pickup_aggro():
    pass


@bot.command(name='attack')
async def attack_response(context, *args):
    if len(args) < 1:
        return

    lock.acquire()
    try:
        with Session(engine) as session:
            entity = Entity.select_with_reference(session, args[0])
            if entity is None or not isinstance(entity, MonsterInstance):
                return
            if entity.id not in active_monsters:
                active_monsters[entity.id] = {
                    'data': monster_index.index[entity.monster_id],
                    'loop_offset': -1,
                    'aggros': [context.author.id]
                }
            else:
                active_monsters[entity.id]['aggros'] = [context.author.id]
    finally:
        lock.release()


bot.run(TOKEN)
