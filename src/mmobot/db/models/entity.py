from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from .base import Base


class Entity(Base):
    __tablename__ = 'Entities'

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'entity',
        'polymorphic_on': entity_type
    }

    def __repr__(self):
        return f'Entity(id={self.id})'
