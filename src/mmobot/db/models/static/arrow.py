from sqlalchemy import Column, ForeignKey, Integer, String

from mmobot.db.models import Item


class Arrow(Item):
    __tablename__ = 'Arrows'

    id = Column(String(40), ForeignKey('Items.id', ondelete='cascade'), primary_key=True)
    lethality = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'arrow'
    }

    def __repr__(self):
        return f'Arrow(id={self.id})'

    def from_yaml(yaml):
        return Arrow(
            id=yaml['id'],
            weight=yaml['weight'],
            lethality=yaml['lethality'] if 'lethality' in yaml else 0
        )
