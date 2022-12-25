import pytest

from sqlalchemy.orm import Session

from mmobot.db.models import (
    ItemInstance,
    Player,
    PlayerSkill,
    ToolInstance,
    WeaponInstance,
    Zone
)
from mmobot.test.db import (
    init_test_engine
)
from mmobot.utils.crafting import separate_crafting_components


engine = init_test_engine()

@pytest.fixture
def session():
    return Session(engine)


def test_separateCraftingComponents_invalidReference():
    references = ['/123', '/abc', 'nope', '/xyz']
    error_message = separate_crafting_components(references, None)
    assert error_message['error'] == 'nope'


def test_separateCraftingComponents_success():
    references = ['/7', '/1', '/2', '/5', '/3', '/6', '/4']
    player_inventory = [
        ItemInstance(id=1, item_id='stone'),
        ItemInstance(id=3, item_id='iron-ore'),
        ItemInstance(id=4, item_id='stone-bowl'),
        WeaponInstance(id=2, item_id='iron-hammer'),
        ItemInstance(id=200, item_id='not-included')
    ]
    zone_loot = [
        ItemInstance(id=201, item_id='not-included'),
        ToolInstance(id=6, item_id='main-tool'),
        ItemInstance(id=7, item_id='not-included')
    ]
    skills = [PlayerSkill(skill_name='skill', skill_level=15)]
    zone = Zone(channel_name='town-square', loot=zone_loot)
    player = Player(
        id=100,
        equipped_weapon_id=2,
        inventory=player_inventory,
        skills=skills,
        zone=zone
    )
    components = separate_crafting_components(references, player)
    assert 'error' not in components
    assert len(components['ingredients']) == 3
    assert player_inventory[0] in components['ingredients']
    assert player_inventory[1] in components['ingredients']
    assert player_inventory[2] in components['ingredients']
    assert player_inventory[3] not in components['ingredients']
    assert player_inventory[4] not in components['ingredients']
    assert len(components['tools']) == 1
    assert zone_loot[0] not in components['tools']
    assert zone_loot[1] in components['tools']
    assert zone_loot[2] not in components['tools']
    assert components['handheld'] is not None
    assert components['handheld'] == player_inventory[3]
    assert len(components['skills']) == 1
    assert components['skills'][0] == skills[0]
