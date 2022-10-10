from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from mmobot.db.models import Item


class Weapon(Item):
    __tablename__ = 'Weapons'

    id = Column(String(40), ForeignKey('Items.id', ondelete='cascade'), primary_key=True)
    weapon_type = Column(String(20))
    strength = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'weapon'
    }

    def __repr__(self):
        return f'Weapon(name={self.name})'
