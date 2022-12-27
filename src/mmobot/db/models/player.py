from datetime import date

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import select
from sqlalchemy import String
from sqlalchemy.orm import relationship

from mmobot.db.models import Agent


class Player(Agent):
    __tablename__ = 'Players'

    id = Column(Integer, ForeignKey('Agents.id', ondelete='cascade'), primary_key=True)
    name = Column(String(40), unique=True, nullable=False)
    discord_id = Column(String(40), nullable=False)
    ancestry = Column(Integer)
    birthday = Column(DateTime)
    deathday = Column(DateTime)
    parent_name = Column(String(40))

    stats_id = Column(Integer, ForeignKey('PlayerStats.id'), unique=True, nullable=False)
    stats = relationship('PlayerStats', uselist=False)
    skills = relationship('PlayerSkill')

    inventory = relationship(
        'ItemInstance',
        order_by='ItemInstance.id',
        foreign_keys='ItemInstance.player_id'
    )

    last_learned = Column(DateTime, default=date.fromtimestamp(1))
    last_taught = Column(DateTime, default=date.fromtimestamp(1))

    # The equipped item fields implicitly point to WeaponInstances.
    # However, we do not set a foreign key to avoid creating a cycle.
    # Instead, we will search Player.inventory for the item we need
    # and update the equipped_ids when items are dropped/given.
    equipped_weapon_id = Column(Integer)
    equipped_attire_id = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'player',
        'inherit_condition': id == Agent.id
    }

    def __repr__(self):
        return f'Player(name={self.name})'

    def select_with_discord_id(session, discord_id):
        get_player_statement = (
            select(Player)
            .where(Player.discord_id == discord_id)
            .where(Player.is_active)
        )
        return session.scalars(get_player_statement).one_or_none()
