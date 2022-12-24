from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import String

from ..base import Base


class Nonsolid(Base):
    __tablename__ = 'Nonsolids'

    id = Column(String(40), primary_key=True)
    nonsolid_type = Column(String(20))
    size = Column(Float)
    weight = Column(Float)

    __mapper_args__ = {
        'polymorphic_identity': 'nonsolid',
        'polymorphic_on': nonsolid_type
    }

    def __repr__(self):
        return f'Nonsolid(id={self.id})'
