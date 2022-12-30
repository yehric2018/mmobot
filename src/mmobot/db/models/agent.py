from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from mmobot.db.models import Entity
from mmobot.utils.entities import convert_int_to_alphanum


class Agent(Entity):
    __tablename__ = 'Agents'

    id = Column(Integer, ForeignKey('Entities.id', ondelete='cascade'), primary_key=True)
    is_active = Column(Boolean)

    hp = Column(Float)
    endurance = Column(Float)

    max_hp = Column(Integer)
    max_endurance = Column(Integer)
    strength = Column(Integer)
    mobility = Column(Integer)

    guarding_entity_id = Column(Integer, ForeignKey('Entities.id'))
    guarding_entity = relationship(
        'Entity',
        foreign_keys='Agent.guarding_entity_id',
        back_populates='guardians'
    )

    inventory_weight = Column(Float)

    __mapper_args__ = {
        'polymorphic_identity': 'agent',
        'inherit_condition': id == Entity.id
    }

    def get_name(self):
        return f'/{convert_int_to_alphanum(self.id)}'

    def get_burden(self):
        return max(0, self.inventory_weight - self.real_strength()) / (self.strength * 0.2)

    def hp_endurance_ratio(self):
        return (self.hp + self.endurance) / (self.max_hp + self.max_endurance)

    def real_strength(self):
        return self.strength * self.hp_endurance_ratio()
