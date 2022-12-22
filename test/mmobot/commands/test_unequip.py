import pytest
from sqlalchemy.orm import Session

from mmobot.commands import unequip_logic
from mmobot.db.models.player import Player
from mmobot.test.db import (
    add_player,
    add_weapon_instance,
    delete_all_entities,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext


MESSAGE_HOW_TO_USE = 'Please indicate which item you would like to unequip, '\
            'for example: !unequip item'
MESSAGE_UNEQUIP_NAME_SUCCESS = 'Unequipped desert-scimitar'


engine = init_test_engine()


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    add_player(session, Player(
        id=1,
        name='player',
        discord_id=100,
        is_active=True,
        equipped_weapon_id=200,
        equipped_attire_id=208
    ))
    yield
    delete_all_entities(session)


@pytest.fixture(autouse=True)
def setup_item(session, prepare_database):
    add_weapon_instance(session, 200, 1, 'desert-scimitar')
    add_weapon_instance(session, 208, 1, 'knights-armor')


@pytest.fixture
def unequip_context(member, town_square_channel, test_guild):
    return MockContext(member, town_square_channel, test_guild)


@pytest.mark.asyncio
async def test_commandUnequip_weaponWithName(unequip_context, session):
    await unequip_logic(unequip_context, ['desert-scimitar'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == MESSAGE_UNEQUIP_NAME_SUCCESS
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id is None


@pytest.mark.asyncio
async def test_commandUnequip_weaponWithIndex(unequip_context, session):
    await unequip_logic(unequip_context, ['0'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == MESSAGE_UNEQUIP_NAME_SUCCESS
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id is None


@pytest.mark.asyncio
async def test_commandUnequip_weaponWithId(unequip_context, session):
    await unequip_logic(unequip_context, ['/5k'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == 'Unequipped /5k'
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id is None


@pytest.mark.asyncio
async def test_commandUnequip_attireWithId(unequip_context, session):
    await unequip_logic(unequip_context, ['/5s'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == 'Unequipped /5s'
    player = get_player_with_name(session, 'player')
    assert player.equipped_attire_id is None


@pytest.mark.asyncio
async def test_commandUnequip_notInZone(unequip_context, non_zone_channel):
    unequip_context.channel = non_zone_channel
    await unequip_logic(unequip_context, ['desert-scimitar'], engine)
    assert len(unequip_context.channel.messages) == 0


@pytest.mark.asyncio
async def test_commandUnequip_noArgsProvided(unequip_context, session):
    await unequip_logic(unequip_context, [], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == MESSAGE_HOW_TO_USE
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id is not None


@pytest.mark.asyncio
async def test_commandUnequip_weaponNameNotEquipped(unequip_context, session):
    update_player(session, 1, {'equipped_weapon_id': 900})
    await unequip_logic(unequip_context, ['desert-scimitar'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == 'desert-scimitar is not equipped'
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 900


@pytest.mark.asyncio
async def test_commandUnequip_weaponIndexNotEquipped(unequip_context, session):
    update_player(session, 1, {'equipped_weapon_id': 900})
    await unequip_logic(unequip_context, ['0'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == 'desert-scimitar is not equipped'
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 900


@pytest.mark.asyncio
async def test_commandUnequip_weaponIdNotEquipped(unequip_context, session):
    update_player(session, 1, {'equipped_weapon_id': 900})
    await unequip_logic(unequip_context, ['/5k'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == '/5k is not equipped'
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 900
