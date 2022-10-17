from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from mmobot.db.models import Item


class Attire(Item):
    __tablename__ = 'Attires'

    id = Column(String(40), ForeignKey('Items.id', ondelete='cascade'), primary_key=True)
    coverage = Column(Integer)
    armor = Column(Integer)
    warmth = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'attire'
    }

    def __repr__(self):
        return f'Attire(id={self.id})'
