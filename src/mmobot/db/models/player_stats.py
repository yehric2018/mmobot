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
    experience = Column(Integer, default=0)
    magic_number = Column(Integer)
    fighting_skill = Column(Integer, default=0)
    hunting_skill = Column(Integer, default=0)
    mining_skill = Column(Integer, default=0)
    cooking_skill = Column(Integer, default=0)
    crafting_skill = Column(Integer, default=0)
