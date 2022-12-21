import asyncio

from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.db.models import Player, PlayerStats
from mmobot.utils.players import handle_incapacitation


async def decrement_hp(client, engine):
    '''
    This job is scheduled to run at set time throughout the day to decrement the HP
    of players over time.
    '''
    incapacitated_players = []
    with Session(engine) as session:
        get_player_statement = (
            select(Player)
            .where(Player.is_active)
            .where(Player.stats.has(PlayerStats.hp > 0))
        )
        for player in session.scalars(get_player_statement):
            player.stats.hp -= 1
            if player.stats.hp == 0:
                incapacitated_players.append(player)

        session.commit()

        async def incapacitate(player):
            return await handle_incapacitation(player, engine, client)
        await asyncio.gather(*map(incapacitate, incapacitated_players))
