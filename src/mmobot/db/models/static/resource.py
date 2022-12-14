from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String

from mmobot.db.models import Item


class Resource(Item):
    __tablename__ = 'Resources'

    id = Column(String(40), ForeignKey('Items.id', ondelete='cascade'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'resource'
    }

    def __repr__(self):
        return f'Resource(id={self.id})'

    def from_yaml(yaml):
        return Resource(
            id=yaml['id'],
            weight=yaml['weight']
        )
