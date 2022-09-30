from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from mmobot.db.models import Entity


class ItemInstance(Entity):
    __tablename__ = 'ItemInstances'

    id = Column(Integer, ForeignKey('Entities.id'), primary_key=True)
    player_id = Column(Integer, ForeignKey('Players.id'))
    zone_name = Column(String(40), ForeignKey('Zones.channel_name'))
    item_id = Column(String(40), ForeignKey('Items.id'))
    item = relationship('Item')

    __mapper_args__ = {
        'polymorphic_identity': 'item'
    }

    def __repr__(self):
        return f'ItemInstance(id={self.id})'
