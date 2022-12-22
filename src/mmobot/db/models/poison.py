from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from mmobot.db.models import Nonsolid


class Poison(Nonsolid):
    __tablename__ = 'Poisons'

    id = Column(String(40), ForeignKey('Nonsolids.id', ondelete='cascade'), primary_key=True)
    damage = Column(Integer)
    duration = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'poison'
    }

    def __repr__(self):
        return f'Poison(id={self.id})'
