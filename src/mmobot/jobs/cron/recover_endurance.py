from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Player


def recover_endurance(engine):
    '''
    This job is scheduled to run at set time throughout the day to increment the endurance
    of players over time.
    '''
    with Session(engine) as session:
        get_player_statement = (
            select(Player)
            .where(Player.is_active)
            .where(Player.endurance < Player.max_endurance)
        )
        for player in session.scalars(get_player_statement):
            player.endurance += 1

        session.commit()
