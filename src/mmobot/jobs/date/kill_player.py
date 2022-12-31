import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from mmobot.db import initialize_engine
from mmobot.db.models import Player


load_dotenv()
AFTERLIFE_CHANNEL_ID = os.getenv('AFTERLIFE_CHANNEL_ID')
engine = initialize_engine()


def clear_inventory(player):
    for item in player.inventory:
        item.drop_into_zone(player.zone)
    player.inventory_weight = 0


async def kill_player(player_discord_id, client):
    '''
    Checks if the given player is incapacitated (hp = 0 or satiety = 0).
    If so, this job was triggered 2 minutes from when they were first incapacitated,
    so this job will kill the player by doing the following:
    1. Set their is_active to False, and ensure they are not already dead
    2. Make an announcement in their channel that they are dead
    3. Move their location from the zone to the afterlife
    '''
    print('Killing the player')
    with Session(engine) as session:
        player = Player.select_with_discord_id(player_discord_id)
        if player is None:
            return
        if player.hp > 0:
            return
        user = client.get_user(player_discord_id)

        current_channel = await client.fetch_channel(player.zone.channel_id)
        await current_channel.set_permissions(user, read_messages=False, send_messages=False)
        await current_channel.send(f'{player.name} is dead')

        afterlife_channel = await client.fetch_channel(AFTERLIFE_CHANNEL_ID)
        await afterlife_channel.set_permissions(user, read_messages=True, send_messages=True)
        await afterlife_channel.send(f'{player.name} has arrived')

        player.is_active = False
        clear_inventory(player)
        session.commit()
