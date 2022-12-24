from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from mmobot.db.models import Item


class Tool(Item):
    __tablename__ = 'Tools'

    id = Column(String(40), ForeignKey('Items.id', ondelete='cascade'), primary_key=True)
    tool_type = Column(String(20))
    craft = Column(Integer, default=0)

    __mapper_args__ = {
        'polymorphic_identity': 'tool'
    }

    def __repr__(self):
        return f'Tool(id={self.id})'

    def from_yaml(yaml):
        return Tool(
            id=yaml['id'],
            tool_type=yaml['tool_type'],
            size=yaml['size'],
            weight=yaml['weight'],
            craft=yaml['craft']
        )
