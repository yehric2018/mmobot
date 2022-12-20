from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db import initialize_engine
from mmobot.db.models import Player


engine = initialize_engine()


def clear_inventory(player):
    for item in player.inventory:
        item.drop_into_zone(player.zone)


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
        user = client.get_user(player_discord_id)

        left_world = False
        entered_afterlife = True
        for channel in client.get_all_channels():
            if channel.name == player.zone:
                await channel.set_permissions(user, read_messages=False, send_messages=False)
                await channel.send(f'{player.name} is dead')
                left_world = True
            if channel.name == 'afterlife':
                await channel.set_permissions(user, read_messages=True, send_messages=True)
                await channel.send(f'{player.name} has arrived')
                entered_afterlife = True
            if left_world and entered_afterlife:
                player.is_active = False
                clear_inventory(player)
                session.commit()
                return
        # If we reach the end here, we didn't move channels...we should throw an error here later
