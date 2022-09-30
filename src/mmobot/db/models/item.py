from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from .base import Base


class Item(Base):
    __tablename__ = 'Items'

    id = Column(String(40), primary_key=True)
    item_type = Column(String(20))
    size = Column(Integer)
    weight = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'item',
        'polymorphic_on': item_type
    }

    def __repr__(self):
        return f'Item(name={self.name})'
