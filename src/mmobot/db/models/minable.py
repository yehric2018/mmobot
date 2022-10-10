from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from mmobot.db.models import Interaction


class Minable(Interaction):
    __tablename__ = 'Minables'

    id = Column(Integer, ForeignKey('Interactions.id', ondelete='cascade'), primary_key=True)
    stone_comp = Column(Integer)
    coal_comp = Column(Integer)
    iron_comp = Column(Integer)
    silver_comp = Column(Integer)
    gold_comp = Column(Integer)
    diamond_comp = Column(Integer)
    platinum_comp = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'minable'
    }

    def __repr__(self):
        return f'Minable(id={self.id})'
