from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from mmobot.db.models import Nonsolid


class FluidFood(Nonsolid):
    __tablename__ = 'FluidFoods'

    id = Column(String(40), ForeignKey('Nonsolids.id', ondelete='cascade'), primary_key=True)
    hp_recover = Column(Integer, default=0)
    endurance_recover = Column(Integer, default=0)
    impairment = Column(Integer, default=0)
    impairment_duration = Column(Integer, default=0)
    hp_relief = Column(Integer, default=0)
    relief_duration = Column(Integer, default=0)
    endurance_boost = Column(Integer, default=0)
    boost_duration = Column(Integer, default=0)

    __mapper_args__ = {
        'polymorphic_identity': 'fluid_food'
    }

    def __repr__(self):
        return f'FluidFood(id={self.id})'

    def from_yaml(yaml):
        return FluidFood(
            id=yaml['id'],
            weight=FluidFood._handle_field(yaml, 'weight'),
            hp_recover=FluidFood._handle_field(yaml, 'hp_recover'),
            endurance_recover=FluidFood._handle_field(yaml, 'endurance_recover'),
            impairment=FluidFood._handle_field(yaml, 'impairment'),
            impairment_duration=FluidFood._handle_field(yaml, 'impairment_duration'),
            hp_relief=FluidFood._handle_field(yaml, 'hp_relief'),
            relief_duration=FluidFood._handle_field(yaml, 'relief_duration'),
            endurance_boost=FluidFood._handle_field(yaml, 'endurance_boost'),
            boost_duration=FluidFood._handle_field(yaml, 'boost_duration')
        )

    def _handle_field(yaml, key):
        return yaml[key] if key in yaml else 0
