from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from mmobot.db.models import Item


class Weapon(Item):
    __tablename__ = 'Weapons'

    id = Column(String(40), ForeignKey('Items.id', ondelete='cascade'), primary_key=True)
    weapon_type = Column(String(20))
    lethality = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'weapon'
    }

    def __repr__(self):
        return f'Weapon(id={self.id})'
    
    def from_yaml(yaml):
        return Weapon(
            id=yaml['id'],
            size=yaml['size'],
            weight=yaml['weight'],
            weapon_type=yaml['weapon_type'],
            lethality=yaml['lethality']
        )
