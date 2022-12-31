from sqlalchemy import Column
from sqlalchemy import DDL
from sqlalchemy import event
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import select
from sqlalchemy import Sequence
from sqlalchemy import String
from sqlalchemy.orm import relationship

from .base import Base
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id


class Entity(Base):
    __tablename__ = 'Entities'

    id = Column(
        Integer,
        Sequence('entity_id_seq', start=5000, increment=1),
        primary_key=True
    )
    entity_type = Column(String(20))
    zone_id = Column(Integer, ForeignKey('Zones.id'))
    zone = relationship(
        'Zone',
        foreign_keys='Entity.zone_id',
        overlaps='interactions,loot,monsters'
    )
    guardians = relationship('Agent', foreign_keys='Agent.guarding_entity_id')

    __mapper_args__ = {
        'polymorphic_identity': 'entity',
        'polymorphic_on': entity_type
    }

    def __repr__(self):
        return f'Entity(id={self.id})'

    def select_with_reference(session, entity_id, channel_id=None):
        if is_entity_id(str(entity_id)):
            entity_id = convert_alphanum_to_int(entity_id)
        get_entity_statement = (
            select(Entity)
            .where(Entity.id == entity_id)
        )
        if channel_id is not None:
            get_entity_statement = get_entity_statement.where(
                Entity.zone.has(channel_id=channel_id)
            )
        return session.scalars(get_entity_statement).one_or_none()


event.listen(
    Entity.__table__,
    "after_create",
    DDL("ALTER TABLE %(table)s AUTO_INCREMENT = 5001;")
)
