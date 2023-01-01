from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from mmobot.db.models import ItemInstance


class SolidFoodInstance(ItemInstance):
    __tablename__ = 'SolidFoodInstances'

    id = Column(Integer, ForeignKey('ItemInstances.id', ondelete='cascade'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'solid_food'
    }
