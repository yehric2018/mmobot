from sqlalchemy import Boolean, Column, Integer, String

from ..base import Base


class Monster(Base):
    __tablename__ = 'Monsters'

    id = Column(String(40), primary_key=True)
    hp = Column(Integer)
    endurance = Column(Integer)
    strength = Column(Integer)
    mobility = Column(Integer)
    armor = Column(Integer)

    fighting_skill = Column(Integer)
    evasion = Column(Integer)

    loop_cooldown = Column(Integer)
    aggro_chance = Column(Integer)
    fights_back = Column(Boolean)

    def from_yaml(yaml):
        return Monster(
            id=yaml['id'],
            hp=yaml['hp'],
            endurance=yaml['endurance'],
            strength=yaml['strength'],
            mobility=yaml['mobility'],
            armor=yaml['armor'],
            loop_cooldown=yaml['loop_cooldown'],
            aggro_chance=yaml['aggro_chance'],
            fights_back=yaml['fights_back'],
            fighting_skill=yaml['fighting_skill'],
            evasion=yaml['evasion']
        )
