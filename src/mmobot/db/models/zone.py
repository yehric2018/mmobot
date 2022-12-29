from sqlalchemy import Column, Integer, String
from sqlalchemy import select
from sqlalchemy.orm import relationship

from .base import Base


class Zone(Base):
    __tablename__ = 'Zones'

    id = Column(Integer, primary_key=True)
    channel_id = Column(String(40), unique=True)
    channel_name = Column(String(40))
    # minizone_parent = Column(String(40), ForeignKey('Zones.channel_name', ondelete='cascade'))

    # navigation = relationship('ZonePath', foreign_keys='ZonePath.start_zone_name')
    # minizones = relationship('Zone', foreign_keys='Zone.minizone_parent')
    interactions = relationship('Interaction', foreign_keys='Interaction.zone_id')
    loot = relationship('ItemInstance', foreign_keys='ItemInstance.zone_id')

    def __repr__(self):
        return f'Zone({self.channel_name})'

    def select_with_channel_id(session, id):
        get_zone_statement = select(Zone).where(Zone.channel_id == id)
        return session.scalars(get_zone_statement).one_or_none()

    def select_with_channel_name(session, channel_name):
        get_zone_statement = select(Zone).where(Zone.channel_name == channel_name)
        return session.scalars(get_zone_statement).one_or_none()
