from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db import initialize_engine
from mmobot.db.models import Player, PlayerStats
from mmobot.utils.players import handle_incapacitation


engine = initialize_engine()


def decrement_hp(client, event_scheduler):
    '''
    This job is scheduled to run at set time throughout the day to decrement the HP
    of players over time.
    '''
    with Session(engine) as session:
        get_player_statement = (
            select(Player)
            .where(Player.is_active)
            .where(Player.stats.has(PlayerStats.hp > 0))
        )
        for player in session.scalars(get_player_statement):
            player.stats.hp -= 1
            handle_incapacitation(player, event_scheduler, client)

        session.commit()
