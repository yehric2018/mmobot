from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from mmobot.db.models import Item


class SolidFood(Item):
    __tablename__ = 'SolidFoods'

    id = Column(String(40), ForeignKey('Items.id', ondelete='cascade'), primary_key=True)
    hp_recover = Column(Integer)
    endurance_recover = Column(Integer)
    impairment = Column(Integer)
    impairment_duration = Column(Integer)
    hp_relief = Column(Integer)
    relief_duration = Column(Integer)
    endurance_boost = Column(Integer)
    boost_duration = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'solid_food'
    }

    def __repr__(self):
        return f'SolidFood(id={self.id})'

    def from_yaml(yaml):
        return SolidFood(
            id=yaml['id'],
            weight=yaml['weight'],
            hp_recover=yaml['hp_recover'],
            endurance_recover=yaml['endurance_recover'],
            impairment=yaml['impairment'],
            impairment_duration=yaml['impairment_duration'],
            hp_relief=yaml['hp_relief'],
            relief_duration=yaml['relief_duration'],
            endurance_boost=yaml['endurance_boost'],
            boost_duration=yaml['boost_duration']
        )
