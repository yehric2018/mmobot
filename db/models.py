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
    "Inventory",
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('player_name', ForeignKey('Players.name')),
    Column('item_id', ForeignKey('Items.id')),
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
    experience = Column(Integer, default=0)
    magic_number = Column(Integer)
    fighting_skill = Column(Integer, default=0)
    hunting_skill = Column(Integer, default=0)
    mining_skill = Column(Integer, default=0)
    cooking_skill = Column(Integer, default=0)
    crafting_skill = Column(Integer, default=0)

    equipped_weapon = Column(String(40), ForeignKey('Weapons.id'))
    equipped_attire = Column(String(40))
    equipped_accessory = Column(String(40))
    inventory = relationship(
        "Item",
        order_by=inventory_table.columns.id,
        secondary=inventory_table
    )

    guarding = Column(String(100))
    last_attack = Column(DateTime)
    last_location = Column(String(100))

    def __repr__(self):
        return f'Player(name={self.name})'

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

    def __repr__(self):
        return f'Item(name={self.name})'

class Weapon(Item):
    __tablename__ = 'Weapons'
    id = Column(String(40), ForeignKey('Items.id'), primary_key=True)
    weapon_type = Column(String(20))
    strength = Column(Integer)
    
    __mapper_args__ = {
        'polymorphic_identity': 'weapon'
    }

    def __repr__(self):
        return f'Weapon(name={self.name})'