from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import relationship

from .base import Base


class Zone(Base):
    __tablename__ = 'Zones'

    channel_name = Column(String(40), primary_key=True)
    navigation = relationship('ZonePath', foreign_keys='ZonePath.start_zone_name')

    def __repr__(self):
        return f'Zone({self.channel_name})'
