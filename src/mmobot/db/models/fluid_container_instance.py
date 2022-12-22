from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from mmobot.db.models import ItemInstance


class FluidContainerInstance(ItemInstance):
    __tablename__ = 'FluidContainerInstances'

    id = Column(Integer, ForeignKey('ItemInstances.id', ondelete='cascade'), primary_key=True)
    nonsolid_id = Column(String(40), ForeignKey('Nonsolids.id'))
    units = Column(Integer)
    poison_id = Column(String(40), ForeignKey('Poisons.id'))

    nonsolid = relationship(
        'Nonsolid',
        uselist=False,
        foreign_keys='FluidContainerInstance.nonsolid_id'
    )
    poison = relationship(
        'Poison',
        uselist=False,
        foreign_keys='FluidContainerInstance.poison_id'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'fluid_container',
        'inherit_condition': id == ItemInstance.id
    }
