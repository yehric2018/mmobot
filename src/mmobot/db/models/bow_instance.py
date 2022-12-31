from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from mmobot.db.models import WeaponInstance


class BowInstance(WeaponInstance):
    __tablename__ = 'BowInstances'

    id = Column(Integer, ForeignKey('WeaponInstances.id', ondelete='cascade'), primary_key=True)
    arrow_id = Column(Integer, ForeignKey('ArrowInstances.id'))
    arrow = relationship('ArrowInstance', foreign_keys='BowInstance.arrow_id')

    __mapper_args__ = {
        'polymorphic_identity': 'bow'
    }
