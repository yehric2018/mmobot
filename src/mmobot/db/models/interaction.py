from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from mmobot.db.models import Entity


class Interaction(Entity):
    __tablename__ = 'Interactions'

    id = Column(Integer, ForeignKey('Entities.id'), primary_key=True)
    interaction_type = Column(String(20))
    zone = Column(String(40), ForeignKey('Zones.channel_name'))

    __mapper_args__ = {
        'polymorphic_identity': 'interaction'
    }

    def __repr__(self):
        return f'Interaction(id={self.id})'
