from ast import For
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

inventory_table = Table(
    "Inventories",
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('player_name', ForeignKey('Players.name')),
    Column('item_id', ForeignKey('Items.id')),
    Column('quantity', Integer)
)

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
    inventory = relationship( "Item", secondary=inventory_table)

    guarding = Column(String(100))
    last_attack = Column(DateTime)
    last_location = Column(String(100))

    def __repr__(self):
        return f'Player(nickname={self.nickname})'

class Item(Base):
    __tablename__ = 'Items'

    id = Column(String(40), primary_key=True)
    name = Column(String(100))
    item_type = Column(String(20))
    size = Column(Integer)
    weight = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'item',
        'polymorphic_on': item_type
    }

class Weapon(Item):
    __tablename__ = 'Weapons'
    id = Column(String(40), ForeignKey("Items.id"), primary_key=True)
    weapon_type = Column(String(20))
    strength = Column(Integer)
    
    __mapper_args__ = {
        'polymorphic_identity': 'weapon'
    }