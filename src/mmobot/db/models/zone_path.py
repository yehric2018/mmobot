from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from .base import Base


class ZonePath(Base):
    __tablename__ = 'ZonePaths'

    start_zone_name = Column(String(40), ForeignKey('Zones.channel_name'), primary_key=True)
    end_zone_name = Column(String(40), ForeignKey('Zones.channel_name'), primary_key=True)
    distance = Column(Integer)
    guardable = Column(Boolean)
    lockable = Column(Boolean)

    def __repr__(self):
        return f'ZonePath({self.start_zone_name} to {self.end_zone_name})'
