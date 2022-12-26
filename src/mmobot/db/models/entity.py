from sqlalchemy import Column
from sqlalchemy import DDL
from sqlalchemy import event
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import String

from .base import Base


class Entity(Base):
    __tablename__ = 'Entities'

    id = Column(
        Integer,
        Sequence('entity_id_seq', start=5000, increment=1),
        primary_key=True
    )
    entity_type = Column(String(20))
    zone = Column(String(40), ForeignKey('Zones.channel_name'))

    __mapper_args__ = {
        'polymorphic_identity': 'entity',
        'polymorphic_on': entity_type
    }

    def __repr__(self):
        return f'Entity(id={self.id})'


event.listen(
    Entity.__table__,
    "after_create",
    DDL("ALTER TABLE %(table)s AUTO_INCREMENT = 5001;")
)
