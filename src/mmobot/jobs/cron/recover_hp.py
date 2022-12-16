from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Player, PlayerStats


def recover_hp(engine):
    '''
    This job is scheduled to run at set time throughout the day to increment the HP
    of players over time.
    '''
    with Session(engine) as session:
        get_player_statement = (
            select(Player)
            .where(Player.is_active)
            .where(Player.stats.has(PlayerStats.hp < PlayerStats.max_hp))
        )
        for player in session.scalars(get_player_statement):
            player.stats.hp += 1

        session.commit()
