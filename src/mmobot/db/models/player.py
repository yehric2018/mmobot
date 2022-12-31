from datetime import date

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import select
from sqlalchemy import String
from sqlalchemy.orm import relationship

from mmobot.constants import WEAPONLESS_LETHALITY
from mmobot.db.models import Agent


class Player(Agent):
    __tablename__ = 'Players'

    id = Column(Integer, ForeignKey('Agents.id', ondelete='cascade'), primary_key=True)
    name = Column(String(40), unique=True, nullable=False)
    discord_id = Column(String(40), nullable=False)
    ancestry = Column(Integer)
    birthday = Column(DateTime)
    deathday = Column(DateTime)
    parent_name = Column(String(40))

    skills = relationship('PlayerSkill')
    inventory = relationship(
        'ItemInstance',
        order_by='ItemInstance.id',
        foreign_keys='ItemInstance.owner_id'
    )

    last_learned = Column(DateTime, default=date.fromtimestamp(1))
    last_taught = Column(DateTime, default=date.fromtimestamp(1))
    stat_points = Column(Integer, default=0)
    skill_points = Column(Integer, default=0)

    # The equipped item fields implicitly point to WeaponInstances.
    # However, we do not set a foreign key to avoid creating a cycle.
    # Instead, we will search Player.inventory for the item we need
    # and update the equipped_ids when items are dropped/given.
    equipped_weapon_id = Column(Integer)
    equipped_attire_id = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'player',
        'inherit_condition': id == Agent.id
    }

    def get_armor(self):
        attire = self.get_equipped_attire()
        return attire.armor if attire is not None else 0

    def get_attack_damage(self):
        weapon_instance = self.get_equipped_weapon()
        if weapon_instance is None:
            return WEAPONLESS_LETHALITY * (self.strength / 100) * self.hp_endurance_ratio()
        weapon = weapon_instance.item
        return weapon.lethality * (self.strength / 100) * self.hp_endurance_ratio()

    def get_defense_score(self):
        weapon_instance = self.get_equipped_weapon()
        weapon_range = weapon_skill = 0
        if weapon_instance is not None:
            weapon_range = weapon_instance.item.range
            weapon_skill = self.get_weapon_skill(weapon_instance.item)
        fighting_skill = self.get_fighting_skill()
        evasion_skill = self.get_evasion_skill()
        raw_score = fighting_skill + weapon_skill + evasion_skill + weapon_range
        return raw_score * self.hp_endurance_ratio()

    def get_equipped_attire(self):
        for item_instance in self.inventory:
            if item_instance.id == self.equipped_attire_id:
                return item_instance
        return None

    def get_equipped_weapon(self):
        for item_instance in self.inventory:
            if item_instance.id == self.equipped_weapon_id:
                return item_instance
        return None

    def get_evasion_skill(self):
        skill_level = self.get_skill_level('evasion')
        return skill_level

    def get_fighting_skill(self):
        skill_level = self.get_skill_level('fighting')
        return skill_level

    def get_offense_score(self):
        weapon_instance = self.get_equipped_weapon()
        weapon_range = weapon_skill = 0
        if weapon_instance is not None:
            weapon_range = weapon_instance.item.range
            weapon_skill = self.get_weapon_skill(weapon_instance.item)
        fighting_skill = self.get_fighting_skill()
        raw_score = fighting_skill + weapon_skill + weapon_range
        return raw_score * self.hp_endurance_ratio()

    def get_skill_level(self, skill_name):
        for skill in self.skills:
            if skill.skill_name == skill_name:
                return skill.skill_level
        return 0

    def get_weapon_skill(self, weapon=None):
        if weapon is None:
            weapon_instance = self.get_equipped_weapon()
            if weapon_instance is None:
                return 0
            weapon = weapon_instance.item
        if weapon.weapon_type == 'sword':
            return self.get_skill_level('sword-mastery')
        elif weapon.weapon_type == 'spear':
            return self.get_skill_level('spear-mastery')
        elif weapon.weapon_type == 'axe':
            return self.get_skill_level('axe-mastery')
        return 0

    def __repr__(self):
        return f'Player(name={self.name})'

    def select_with_discord_id(session, discord_id, channel_id=None):
        get_player_statement = (
            select(Player)
            .where(Player.discord_id == discord_id)
            .where(Player.is_active)
        )
        if channel_id is not None:
            get_player_statement = get_player_statement.where(
                Player.zone.has(channel_id=channel_id)
            )
        return session.scalars(get_player_statement).one_or_none()

    def select_with_discord_name(session, discord_name, channel_id=None):
        get_player_statement = (
            select(Player)
            .where(Player.name == discord_name)
            .where(Player.is_active)
        )
        if channel_id is not None:
            get_player_statement = get_player_statement.where(
                Player.zone.has(channel_id=channel_id)
            )
        return session.scalars(get_player_statement).one_or_none()
