from sqlalchemy import select
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from mmobot.constants import (
    FIGHTING_DEFENSE_RATIO,
    EVASION_DEFENSE_RATIO,
    MOBILITY_DEFENSE_RATIO
)
from mmobot.db.models import Agent
from mmobot.utils.entities import convert_alphanum_to_int, is_entity_id


class MonsterInstance(Agent):
    __tablename__ = 'MonsterInstances'

    id = Column(Integer, ForeignKey('Agents.id', ondelete='cascade'), primary_key=True)
    monster_id = Column(String(40), ForeignKey('Monsters.id'))

    monster = relationship('Monster')

    __mapper_args__ = {
        'polymorphic_identity': 'monster',
        'inherit_condition': id == Agent.id
    }

    def get_armor(self):
        return self.monster.armor

    def get_attack_damage(self):
        return self.strength

    def get_offense_score(self):
        raw_score = self.monster.fighting_skill
        return raw_score * self.hp_endurance_ratio()

    def get_defense_score(self):
        fighting_skill = self.monster.fighting_skill * FIGHTING_DEFENSE_RATIO
        evasion_skill = self.monster.evasion * EVASION_DEFENSE_RATIO
        mobility = (self.mobility - 100) * MOBILITY_DEFENSE_RATIO
        raw_score = fighting_skill + evasion_skill + mobility
        return raw_score * self.hp_endurance_ratio()

    def get_name(self):
        return f'[{super().get_name()}] {self.monster_id}'

    def create_instance(monster, zone=None):
        return MonsterInstance(
            monster_id=monster.id,
            hp=monster.hp,
            endurance=monster.endurance,
            max_hp=monster.hp,
            max_endurance=monster.endurance,
            strength=monster.strength,
            mobility=monster.mobility,
            zone=zone
        )

    def select_with_reference(session, reference):
        if is_entity_id(str(reference)):
            reference = convert_alphanum_to_int(reference)
        get_monster_statement = (
            select(MonsterInstance)
            .where(MonsterInstance.id == reference)
            .where(MonsterInstance.is_active)
        )
        return session.scalars(get_monster_statement).one_or_none()
