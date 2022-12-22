from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from mmobot.db.models import Item


class FluidContainer(Item):
    __tablename__ = 'FluidContainers'

    id = Column(String(40), ForeignKey('Items.id', ondelete='cascade'), primary_key=True)
    max_capacity = Column(Integer)

    _mapper_args__ = {
        'polymorphic_identity': 'fluid_container'
    }

    def __repr__(self):
        return f'FluidContainer(id={self.id})'

    def from_yaml(yaml):
        return FluidContainer(
            id=yaml['id'],
            size=yaml['size'],
            weight=yaml['weight'],
            max_capacity=yaml['max_capacity']
        )
