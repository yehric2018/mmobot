import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from mmobot.db.models import Player


load_dotenv()
GUILD_ID = int(os.getenv('DISCORD_GUILD'))


async def kill_player(player_discord_id, engine, client):
    '''
    Kill a player once their HP has hit 0 by doing the following:
    1. Set their is_active to False, and ensure they are not already dead
    2. Make an announcement in their channel that they are dead
    3. Move their location from the zone to the afterlife
    '''
    with Session(engine) as session:
        # Check for the player in the database again to make sure we don't double kill them.
        # This might occur is they are attacked while incapacitated.
        # Also check if the player was revived (hp > 0)
        player = Player.select_with_discord_id(player_discord_id)
        if player is None or player.hp > 0:
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
                player.deathday = datetime.now()
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
