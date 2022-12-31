from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from mmobot.constants import BASE_MOVEMENT_COOLDOWN
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
    last_move_time = Column(DateTime, nullable=False)
    retreat_direction = Column(Integer, default=0)

    __mapper_args__ = {
        'polymorphic_identity': 'agent',
        'inherit_condition': id == Entity.id
    }

    def get_remaining_move_cooldown(self, direction):
        if self.last_move_time is None:
            return 0
        cooldown = self.get_movement_cooldown()
        if direction == self.retreat_direction:
            cooldown /= 2
        return max(0, (cooldown - (datetime.now() - self.last_move_time)).total_seconds())

    def get_name(self):
        return f'/{convert_int_to_alphanum(self.id)}'

    def get_armor(self):
        pass

    def get_attack_damage(self):
        pass

    def get_burden(self):
        return max(0, self.inventory_weight - self.real_strength()) / (self.strength * 0.2)

    def get_evasion_skill(self):
        pass

    def get_fighting_skill(self):
        pass

    def get_movement_cooldown(self):
        movement_multiplier = self.hp_endurance_ratio() * self.mobility / 100
        return BASE_MOVEMENT_COOLDOWN / movement_multiplier

    def get_offense_score(self):
        pass

    def hp_endurance_ratio(self):
        return (self.hp + self.endurance) / (self.max_hp + self.max_endurance)

    def real_strength(self):
        return self.strength * self.hp_endurance_ratio()
