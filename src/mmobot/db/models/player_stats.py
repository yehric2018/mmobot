from sqlalchemy import Column
from sqlalchemy import Integer

from .base import Base


class PlayerStats(Base):
    __tablename__ = 'PlayerStats'

    id = Column(Integer, primary_key=True)
    hp = Column(Integer)
    max_hp = Column(Integer)
    armor = Column(Integer)
    mobility = Column(Integer)
    endurance = Column(Integer)
    max_endurance = Column(Integer)
    strength = Column(Integer)
    luck = Column(Integer)
    magic_number = Column(Integer)
    stat_points = Column(Integer, default=0)
    skill_points = Column(Integer, default=0)
