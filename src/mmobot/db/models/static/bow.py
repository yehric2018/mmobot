from sqlalchemy import Column, ForeignKey, String

from mmobot.db.models import Weapon


class Bow(Weapon):
    __tablename__ = 'Bows'

    id = Column(String(40), ForeignKey('Weapons.id', ondelete='cascade'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'bow'
    }

    def __repr__(self):
        return f'Bow(id={self.id})'

    def from_yaml(yaml):
        return Bow(
            id=yaml['id'],
            weight=yaml['weight'],
            lethality=yaml['lethality'] if 'lethality' in yaml else 0,
            range=yaml['range'] if 'range' in yaml else 0,
            craft=0
        )
