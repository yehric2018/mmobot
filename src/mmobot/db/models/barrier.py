from sqlalchemy import Column, ForeignKey, Integer

from mmobot.db.models import Entity


class Barrier(Entity):
    __tablename__ = 'Barriers'

    id = Column(Integer, ForeignKey('Entities.id', ondelete='cascade'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'barrier'
    }
