from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer

from .base import Base


class PlayerSkills(Base):
    __tablename__ = 'PlayerSkills'

    id = Column(Integer, primary_key=True)
    skill_points = Column(Integer, default=0)
    last_learned = Column(DateTime)
    last_taught = Column(DateTime)

    fighting = Column(Integer, default=0)
    marksmanship = Column(Integer, default=0)
    smithing = Column(Integer, default=0)
    farming = Column(Integer, default=0)
    cooking = Column(Integer, default=0)
    fishing = Column(Integer, default=0)
    weaving = Column(Integer, default=0)
    carpentry = Column(Integer, default=0)
    masonry = Column(Integer, default=0)
    medicine = Column(Integer, default=0)
