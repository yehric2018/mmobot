from sqlalchemy import Column, ForeignKey, String
from sqlalchemy import select
from sqlalchemy.orm import relationship

from .base import Base


class Zone(Base):
    __tablename__ = 'Zones'

    channel_name = Column(String(40), primary_key=True)
    minizone_parent = Column(String(40), ForeignKey('Zones.channel_name', ondelete='cascade'))

    navigation = relationship('ZonePath', foreign_keys='ZonePath.start_zone_name')
    minizones = relationship('Zone', foreign_keys='Zone.minizone_parent')
    interactions = relationship('Interaction', foreign_keys='Interaction.zone')
    loot = relationship('ItemInstance', foreign_keys='ItemInstance.zone')

    def __repr__(self):
        return f'Zone({self.channel_name})'

    def select_with_channel_name(session, channel_name):
        get_zone_statement = select(Zone).where(Zone.channel_name == channel_name)
        return session.scalars(get_zone_statement).one_or_none()
