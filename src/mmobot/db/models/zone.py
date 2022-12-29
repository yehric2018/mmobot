from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import select
from sqlalchemy.orm import relationship

from .base import Base


class Zone(Base):
    __tablename__ = 'Zones'

    id = Column(Integer, primary_key=True)
    channel_id = Column(String(40), unique=True)
    channel_name = Column(String(40))
    grid_row = Column(Integer)
    grid_col = Column(Integer)

    north_zone_id = Column(Integer, ForeignKey('Zones.id'))
    north_zone = relationship('Zone', foreign_keys=[north_zone_id], remote_side=[id])
    north_wall_id = Column(Integer, ForeignKey('Barriers.id'))
    north_wall = relationship('Barrier', foreign_keys='Zone.north_wall_id')

    east_zone_id = Column(Integer, ForeignKey('Zones.id'))
    east_zone = relationship('Zone', foreign_keys=[east_zone_id], remote_side=[id])
    east_wall_id = Column(Integer, ForeignKey('Barriers.id'))
    east_wall = relationship('Barrier', foreign_keys='Zone.east_wall_id')

    south_zone_id = Column(Integer, ForeignKey('Zones.id'))
    south_zone = relationship('Zone', foreign_keys=[south_zone_id], remote_side=[id])
    south_wall_id = Column(Integer, ForeignKey('Barriers.id'))
    south_wall = relationship('Barrier', foreign_keys='Zone.south_wall_id')

    west_zone_id = Column(Integer, ForeignKey('Zones.id'))
    west_zone = relationship('Zone', foreign_keys=[west_zone_id], remote_side=[id])
    west_wall_id = Column(Integer, ForeignKey('Barriers.id'))
    west_wall = relationship('Barrier', foreign_keys='Zone.west_wall_id')

    interactions = relationship('Interaction', foreign_keys='Interaction.zone_id')
    loot = relationship('ItemInstance', foreign_keys='ItemInstance.zone_id')

    def can_move_north(self):
        return (self.north_zone_id is not None
                and self.north_wall_id is None
                and self.north_zone.south_wall_id is None)

    def can_move_east(self):
        return (self.east_zone_id is not None
                and self.east_wall_id is None
                and self.east_zone.west_wall_id is None)

    def can_move_south(self):
        return (self.south_zone_id is not None
                and self.south_wall_id is None
                and self.south_zone.north_wall_id is None)

    def can_move_west(self):
        return (self.west_zone_id is not None
                and self.west_wall_id is None
                and self.west_zone.east_wall_id is None)

    def __repr__(self):
        return f'Zone({self.channel_name})'

    def select_with_id(session, id):
        get_zone_statement = select(Zone).where(Zone.id == id)
        return session.scalars(get_zone_statement).one_or_none()

    def select_with_channel_id(session, id):
        get_zone_statement = select(Zone).where(Zone.channel_id == id)
        return session.scalars(get_zone_statement).one_or_none()
