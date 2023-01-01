from sqlalchemy import Column, ForeignKey, Integer

from mmobot.db.models import ItemInstance


class ArrowInstance(ItemInstance):
    __tablename__ = 'ArrowInstances'

    id = Column(Integer, ForeignKey('ItemInstances.id', ondelete='cascade'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'arrow'
    }
