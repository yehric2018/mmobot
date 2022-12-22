from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from mmobot.db.models import Nonsolid


class FluidFood(Nonsolid):
    __tablename__ = 'FluidFoods'

    id = Column(String(40), ForeignKey('Nonsolids.id', ondelete='cascade'), primary_key=True)
    hp_recover = Column(Integer)
    endurance_recover = Column(Integer)
    impairment = Column(Integer)
    impairment_duration = Column(Integer)
    hp_relief = Column(Integer)
    relief_duration = Column(Integer)
    endurance_boost = Column(Integer)
    boost_duration = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'fluid_food'
    }

    def __repr__(self):
        return f'FluidFood(id={self.id})'
