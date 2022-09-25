from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Interval
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Player(Base):
    __tablename__ = 'Players'

    name = Column(String(40), primary_key=True)
    discord_id = Column(String(40))
    ancestry = Column(Integer)
    birthday = Column(DateTime)
    parent_name = Column(String(40))
    is_active = Column(Boolean)
    stance = Column(Integer)
    hp = Column(Integer)
    max_hp = Column(Integer)
    armor = Column(Integer)
    mobility = Column(Integer)
    dexterity = Column(Integer)
    endurance = Column(Integer)
    max_endurance = Column(Integer)
    strength = Column(Integer)
    luck = Column(Integer)
    experience = Column(Integer)
    magic_number = Column(Integer)
    fighting_skill = Column(Integer)
    hunting_skill = Column(Integer)
    mining_skill = Column(Integer)
    cooking_skill = Column(Integer)
    crafting_skill = Column(Integer)
    equipped_weapon = Column(String(100))
    equipped_armor = Column(String(100))
    equipped_accessory = Column(String(100))
    guarding = Column(String(100))
    last_attack = Column(DateTime)
    last_location = Column(String(100))

    def __repr__(self):
        return f'Player(nickname={self.nickname})'

class Item(Base):
    __tablename__ = 'Items'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    item_type = Column(Integer)
    weight = Column(Integer)
    size = Column(Integer)
    duration = Column(Interval)
    hp = Column(Integer)
    max_hp = Column(Integer)
    armor = Column(Integer)
    mobility = Column(Integer)
    dexterity = Column(Integer)
    endurance = Column(Integer)
    max_endurance = Column(Integer)
    strength = Column(Integer)
    luck = Column(Integer)
    can_revive = Column(Boolean)
    cures_poison = Column(Boolean)
    poisoned = Column(Boolean)

    def __repr__(self):
        return f'Player(id={self.id} name={self.name})'
