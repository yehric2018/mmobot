from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.constants import HEALTHY_PLAYER_THRESHOLD
from mmobot.db.models import Player


async def increment_skill_points(engine):
    '''
    This job is scheduled to run at set time throughout the day to increment the endurance
    of players over time.
    '''
    with Session(engine) as session:
        get_player_statement = select(Player).where(Player.is_active)
        for player in session.scalars(get_player_statement):
            if player.stats.hp > HEALTHY_PLAYER_THRESHOLD:
                player.stats.skill_points += 1

        session.commit()
