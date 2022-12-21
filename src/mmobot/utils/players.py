import asyncio
import os
import random

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Player, PlayerStats


load_dotenv()
GUILD_ID = int(os.getenv('DISCORD_GUILD'))


MIN_INITIAL_HP_CAP = 95
MAX_INITIAL_HP_CAP = 105
MIN_INITIAL_ARMOR = 0
MAX_INITIAL_ARMOR = 5
MIN_INITIAL_MOBILITY = 23
MAX_INITIAL_MOBILITY = 27
MIN_INITIAL_DEXTERITY = 23
MAX_INITIAL_DEXTERITY = 27
MIN_INITIAL_ENDURANCE = 95
MAX_INITIAL_ENDURANCE = 105
MIN_INITIAL_STRENGTH = 23
MAX_INITIAL_STRENGTH = 27

MIN_LUCK = 1
MAX_LUCK = 7


def roll_initial_stats():
    hp = random.randint(MIN_INITIAL_HP_CAP, MAX_INITIAL_HP_CAP)
    armor = random.randint(MIN_INITIAL_ARMOR - 4, MAX_INITIAL_ARMOR)
    if armor < 0:
        armor = 0
    mobility = random.randint(MIN_INITIAL_MOBILITY, MAX_INITIAL_MOBILITY)
    dexterity = random.randint(MIN_INITIAL_DEXTERITY, MAX_INITIAL_DEXTERITY)
    endurance = random.randint(MIN_INITIAL_ENDURANCE, MAX_INITIAL_ENDURANCE)
    strength = random.randint(MIN_INITIAL_STRENGTH, MAX_INITIAL_STRENGTH)
    luck = random.randint(MIN_LUCK, MAX_LUCK)

    return PlayerStats(
        hp=hp,
        max_hp=hp,
        armor=armor,
        mobility=mobility,
        dexterity=dexterity,
        endurance=endurance,
        max_endurance=endurance,
        strength=strength,
        luck=luck,
        magic_number=0
    )


async def handle_incapacitation(player, engine, client):
    '''
    Checks if the player has remaining HP. If they do not, schedule them to be killed
    in two minutes.
    '''
    if player.stats.hp <= 0:
        for channel in client.get_all_channels():
            if channel.name == player.zone:
                await channel.send(f'{player.name} is incapacitated')
        await asyncio.sleep(120)
        await kill_player(player.discord_id, engine, client)


async def kill_player(player_discord_id, engine, client):
    '''
    Checks if the given player is incapacitated (hp = 0 or satiety = 0).
    If so, this job was triggered 2 minutes from when they were first incapacitated,
    so this job will kill the player by doing the following:
    1. Set their is_active to False, and ensure they are not already dead
    2. Make an announcement in their channel that they are dead
    3. Move their location from the zone to the afterlife
    '''
    with Session(engine) as session:
        # Check for the player in the database again to make sure we don't double kill them.
        # This might occur is they are attacked while incapacitated.
        get_player_statement = (
            select(Player)
            .where(Player.discord_id == player_discord_id)
            .where(Player.is_active)
        )
        player = session.scalars(get_player_statement).one_or_none()
        if player is None:
            return
        if player.stats.hp > 0:
            return
        guild = client.get_guild(GUILD_ID)
        member = guild.get_member(int(player_discord_id))

        current_channel = None
        afterlife_channel = None
        for channel in client.get_all_channels():
            if channel.name == player.zone:
                current_channel = channel
            if channel.name == 'afterlife':
                afterlife_channel = channel
            if current_channel and afterlife_channel:
                await current_channel.set_permissions(
                    member, read_messages=False, send_messages=False)
                await current_channel.send(f'{player.name} is dead')

                await afterlife_channel.set_permissions(
                    member, read_messages=True, send_messages=True)
                await afterlife_channel.send(f'{player.name} has arrived')

                player.is_active = False
                clear_inventory(player)
                session.commit()
                return
        # If we reach the end here, we didn't move channels...we should throw an error here later
        print('ERROR: Did not find channel with player')


def clear_inventory(player):
    for item in player.inventory:
        item.drop_into_zone(player.zone)


# TODO: Write tests for each of these
def find_item_with_id(inventory, numeric_id):
    for item_instance in inventory:
        if item_instance.id == numeric_id:
            return item_instance


def find_item_with_name(inventory, name):
    for item_instance in inventory:
        if item_instance.item.id == name:
            return item_instance
