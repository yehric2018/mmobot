from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from .base import Base


class PlayerSkill(Base):
    __tablename__ = 'PlayerSkills'

    player_id = Column(Integer, ForeignKey('Players.id'), primary_key=True)
    skill_name = Column(String(20), primary_key=True)
    skill_level = Column(Integer, default=0)

    def __repr__(self):
        return f'PlayerSkill({self.skill_name}:{self.skill_level})'
