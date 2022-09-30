from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

ENTITY_ID = 'Entities.id'
ZONE_CHANNEL_NAME = 'Zones.channel_name'


class Entity(Base):
    __tablename__ = 'Entities'

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'entity',
        'polymorphic_on': entity_type
    }

    def __repr__(self):
        return f'Entity(id={self.id})'


class Player(Entity):
    __tablename__ = 'Players'

    id = Column(Integer, ForeignKey(ENTITY_ID), primary_key=True)
    name = Column(String(40), unique=True, nullable=False)
    discord_id = Column(String(40), nullable=False)
    ancestry = Column(Integer)
    birthday = Column(DateTime)
    deathday = Column(DateTime)
    parent_name = Column(String(40))
    is_active = Column(Boolean)
    stance = Column(Integer)
    stats_id = Column(Integer, ForeignKey('PlayerStats.id'))
    stats = relationship('PlayerStats', uselist=False)

    # equipped_weapon = Column(String(40), ForeignKey('Weapons.id'))
    # equipped_attire = Column(String(40))
    # equipped_accessory = Column(String(40))
    inventory = relationship(
        'ItemInstance',
        order_by='ItemInstance.id',
        foreign_keys='ItemInstance.player_id'
    )

    guarding_entity = Column(Integer, ForeignKey(ENTITY_ID))
    guarding_path = Column(String(40), ForeignKey(ZONE_CHANNEL_NAME))
    last_attack = Column(DateTime)
    last_location = Column(String(40), ForeignKey(ZONE_CHANNEL_NAME))

    __mapper_args__ = {
        'polymorphic_identity': 'player',
        'inherit_condition': id == Entity.id
    }

    def __repr__(self):
        return f'Player(name={self.name})'


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


class ItemInstance(Entity):
    __tablename__ = 'ItemInstances'

    id = Column(Integer, ForeignKey(ENTITY_ID), primary_key=True)
    player_id = Column(Integer, ForeignKey('Players.id'))
    zone_name = Column(String(40), ForeignKey(ZONE_CHANNEL_NAME))
    item_id = Column(String(40), ForeignKey('Items.id'))
    item = relationship('Item')

    __mapper_args__ = {
        'polymorphic_identity': 'item'
    }

    def __repr__(self):
        return f'ItemInstance(id={self.id})'


class WeaponInstance(ItemInstance):
    __tablename__ = 'WeaponInstances'

    id = Column(Integer, ForeignKey('ItemInstances.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'weapon'
    }


class Item(Base):
    __tablename__ = 'Items'

    id = Column(String(40), primary_key=True)
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


class ZonePath(Base):
    __tablename__ = 'ZonePaths'

    start_zone_name = Column(String(40), ForeignKey(ZONE_CHANNEL_NAME), primary_key=True)
    end_zone_name = Column(String(40), ForeignKey(ZONE_CHANNEL_NAME), primary_key=True)
    distance = Column(Integer)
    guardable = Column(Boolean)
    lockable = Column(Boolean)

    def __repr__(self):
        return f'ZonePath({self.start_zone_name} to {self.end_zone_name})'


class Zone(Base):
    __tablename__ = 'Zones'

    channel_name = Column(String(40), primary_key=True)
    navigation = relationship('ZonePath', foreign_keys='ZonePath.start_zone_name')

    def __repr__(self):
        return f'Zone({self.channel_name})'
