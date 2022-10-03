from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from mmobot.db.models import Entity


class Player(Entity):
    __tablename__ = 'Players'

    id = Column(Integer, ForeignKey('Entities.id'), primary_key=True)
    name = Column(String(40), unique=True, nullable=False)
    discord_id = Column(String(40), nullable=False)
    ancestry = Column(Integer)
    birthday = Column(DateTime)
    deathday = Column(DateTime)
    parent_name = Column(String(40))
    is_active = Column(Boolean)
    stance = Column(Integer)
    stats_id = Column(Integer, ForeignKey('PlayerStats.id'))
    stats = relationship('PlayerStats', uselist=False)

    inventory = relationship(
        'ItemInstance',
        order_by='ItemInstance.id',
        foreign_keys='ItemInstance.player_id'
    )

    guarding_entity = Column(Integer, ForeignKey('Entities.id'))
    guarding_path = Column(String(40), ForeignKey('Zones.channel_name'))
    last_attack = Column(DateTime)
    last_location = Column(String(40), ForeignKey('Zones.channel_name'))

    # The equipped item fields implicitly point to WeaponInstances.
    # However, we do not set a foreign key to avoid creating a cycle.
    # Instead, we will search Player.inventory for the item we need
    # and update the equipped_ids when items are dropped/given.
    equipped_weapon_id = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'player',
        'inherit_condition': id == Entity.id
    }

    def __repr__(self):
        return f'Player(name={self.name})'
