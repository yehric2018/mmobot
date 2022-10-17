from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from .base import Base


class PlayerSkillTeaching(Base):
    __tablename__ = 'PlayerSkillTeachings'

    id = Column(Integer, primary_key=True)
    skill = Column(String(20))
    teacher = Column(Integer, ForeignKey('Players.id'))
    learner = Column(Integer, ForeignKey('Players.id'))
    teaching_time = Column(DateTime)
