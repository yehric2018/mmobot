import pytest
from sqlalchemy.orm import Session

from mmobot.commands import guard_logic
from mmobot.db.models import ItemInstance, Player
from mmobot.test.constants import (
    MESSAGE_TEST_PLAYER_INCAPACITATED,
    TEST_ITEM_ENTITY_NUMBER,
    TEST_ITEM_ENTITY_REFERENCE,
    TEST_PLAYER_ENTITY_NUMBER,
    TEST_PLAYER_DISCORD_ID,
    TEST_PLAYER_DISCORD_NAME,
    TEST_PLAYER_ENTITY_NUMBER_2,
    TEST_PLAYER_DISCORD_ID_2,
    TEST_PLAYER_DISCORD_NAME_2,
    TEST_TOWN_SQUARE_ZONE_ID
)
from mmobot.test.db import (
    add_to_database,
    delete_all_entities,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext


engine = init_test_engine()


MESSAGE_GUARD_PLAYER = '<@100> is now guarding <@120>.'
MESSAGE_GUARD_ITEM = '<@100> is now guarding /5k.'
MESSAGE_UNGUARD = '<@100> You are no longer guarding.'
MESSAGE_ITEM_NOT_FOUND = '<@100> Could not find /abc to guard'
MESSAGE_NO_REFERENCE_OR_MENTION = '<@100> Please provide a mention or reference ID to guard.'


@pytest.fixture
def session():
    return Session(engine)


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    add_to_database(session, Player(
        id=TEST_PLAYER_ENTITY_NUMBER,
        name=TEST_PLAYER_DISCORD_NAME,
        discord_id=TEST_PLAYER_DISCORD_ID,
        is_active=True, hp=100,
        zone_id=TEST_TOWN_SQUARE_ZONE_ID
    ))
    add_to_database(session, Player(
        id=TEST_PLAYER_ENTITY_NUMBER_2,
        name=TEST_PLAYER_DISCORD_NAME_2,
        discord_id=TEST_PLAYER_DISCORD_ID_2,
        is_active=True, hp=100,
        zone_id=TEST_TOWN_SQUARE_ZONE_ID
    ))
    add_to_database(session, ItemInstance(
        id=TEST_ITEM_ENTITY_NUMBER,
        item_id='iron-sword',
        zone_id=TEST_TOWN_SQUARE_ZONE_ID
    ))
    yield
    delete_all_entities(session)


@pytest.fixture
def guard_context(member, town_square_channel, test_guild):
    return MockContext(member, town_square_channel, test_guild)


@pytest.mark.asyncio
async def test_commandGuard_guardPlayer(guard_context, session):
    await guard_logic(guard_context, ['<@120>'], engine)
    assert len(guard_context.channel.messages) == 1
    assert guard_context.channel.messages[0] == MESSAGE_GUARD_PLAYER
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.guarding_entity_id == TEST_PLAYER_ENTITY_NUMBER_2
    other_player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME_2)
    assert len(other_player.guardians) == 1
    assert other_player.guardians[0].id == TEST_PLAYER_ENTITY_NUMBER


@pytest.mark.asyncio
async def test_commandGuard_guardItem(guard_context, session):
    await guard_logic(guard_context, [TEST_ITEM_ENTITY_REFERENCE], engine)
    assert len(guard_context.channel.messages) == 1
    assert guard_context.channel.messages[0] == MESSAGE_GUARD_ITEM
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.guarding_entity_id == TEST_ITEM_ENTITY_NUMBER


@pytest.mark.asyncio
async def test_commandGuard_unguard(guard_context, session):
    await guard_logic(guard_context, [], engine)
    assert len(guard_context.channel.messages) == 1
    assert guard_context.channel.messages[0] == MESSAGE_UNGUARD
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.guarding_entity_id is None


@pytest.mark.asyncio
async def test_commandGuard_itemNotInZone(guard_context, session):
    await guard_logic(guard_context, ['/abc'], engine)
    assert len(guard_context.channel.messages) == 1
    assert guard_context.channel.messages[0] == MESSAGE_ITEM_NOT_FOUND
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.guarding_entity_id is None


@pytest.mark.asyncio
async def test_commandGuard_randomWordGiven(guard_context, session):
    await guard_logic(guard_context, ['iron-sword'], engine)
    assert len(guard_context.channel.messages) == 1
    assert guard_context.channel.messages[0] == MESSAGE_NO_REFERENCE_OR_MENTION
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.guarding_entity_id is None


@pytest.mark.asyncio
async def test_commandGuard_playerNotInZone(guard_context, non_zone_channel, session):
    guard_context.channel = non_zone_channel
    await guard_logic(guard_context, [TEST_ITEM_ENTITY_REFERENCE], engine)
    assert len(guard_context.channel.messages) == 0
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.guarding_entity_id is None


@pytest.mark.asyncio
async def test_commandGuard_incapacitated(guard_context, session):
    update_player(session, TEST_PLAYER_ENTITY_NUMBER, {'hp': 0})
    await guard_logic(guard_context, [TEST_ITEM_ENTITY_REFERENCE], engine)
    assert len(guard_context.channel.messages) == 1
    assert guard_context.channel.messages[0] == MESSAGE_TEST_PLAYER_INCAPACITATED
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.guarding_entity_id is None
