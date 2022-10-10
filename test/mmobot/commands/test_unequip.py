import os

import pytest
from dotenv import load_dotenv
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mmobot.commands import unequip_logic
from mmobot.db.models.player import Player
from mmobot.test.db import (
    add_player,
    add_weapon_instance,
    delete_all_entities,
    get_player_with_name,
    update_player
)
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel


load_dotenv()
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_DATABASE_NAME = os.getenv('MYSQL_TEST_DATABASE_NAME')

connection_str = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
    MYSQL_USERNAME,
    MYSQL_PASSWORD,
    MYSQL_HOSTNAME,
    MYSQL_DATABASE_NAME
)

MESSAGE_HOW_TO_USE = 'Please indicate which item you would like to unequip, '\
            'for example: !unequip item'
MESSAGE_UNEQUIP_NAME_SUCCESS = 'Unequipped desert-scimitar'


@pytest.fixture(scope='module')
def engine():
    return create_engine(connection_str)


@pytest.fixture(scope='module')
def session(engine):
    return Session(engine)


@pytest.fixture
def member():
    return MockMember(100, 'player')


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    add_player(session, Player(
        id=1,
        name='player',
        discord_id=100,
        is_active=True,
        equipped_weapon_id=200
    ))
    yield
    delete_all_entities(session)


@pytest.fixture(autouse=True)
def setup_item(session, prepare_database):
    add_weapon_instance(session, 200, 1, 'desert-scimitar')


@pytest_asyncio.fixture
async def channel(member):
    channel = MockTextChannel(1, 'town-square', category='World')
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    return channel


@pytest_asyncio.fixture
async def non_zone_channel():
    return MockTextChannel(2, 'general')


@pytest.fixture
def guild(channel, non_zone_channel):
    guild = MockGuild()
    guild.add_channel(channel)
    guild.add_channel(non_zone_channel)
    return guild


@pytest.fixture
def unequip_context(member, channel, guild):
    return MockContext(member, channel, guild)


@pytest.mark.asyncio
async def test_commandUnequip_weaponWithName(unequip_context, engine, session):
    await unequip_logic(unequip_context, ['desert-scimitar'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == MESSAGE_UNEQUIP_NAME_SUCCESS
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id is None


@pytest.mark.asyncio
async def test_commandUnequip_weaponWithIndex(unequip_context, engine, session):
    await unequip_logic(unequip_context, ['0'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == MESSAGE_UNEQUIP_NAME_SUCCESS
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id is None


@pytest.mark.asyncio
async def test_commandUnequip_weaponWithId(unequip_context, engine, session):
    await unequip_logic(unequip_context, ['/5k'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == 'Unequipped /5k'
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id is None


@pytest.mark.asyncio
async def test_commandUnequip_notInZone(unequip_context, non_zone_channel, engine):
    unequip_context.channel = non_zone_channel
    await unequip_logic(unequip_context, ['desert-scimitar'], engine)
    assert len(unequip_context.channel.messages) == 0


@pytest.mark.asyncio
async def test_commandUnequip_noArgsProvided(unequip_context, engine, session):
    await unequip_logic(unequip_context, [], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == MESSAGE_HOW_TO_USE
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id is not None


@pytest.mark.asyncio
async def test_commandUnequip_weaponNameNotEquipped(unequip_context, engine, session):
    update_player(session, 1, {'equipped_weapon_id': 900})
    await unequip_logic(unequip_context, ['desert-scimitar'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == 'desert-scimitar is not equipped'
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 900


@pytest.mark.asyncio
async def test_commandUnequip_weaponIndexNotEquipped(unequip_context, engine, session):
    update_player(session, 1, {'equipped_weapon_id': 900})
    await unequip_logic(unequip_context, ['0'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == 'desert-scimitar is not equipped'
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 900


@pytest.mark.asyncio
async def test_commandUnequip_weaponIdNotEquipped(unequip_context, engine, session):
    update_player(session, 1, {'equipped_weapon_id': 900})
    await unequip_logic(unequip_context, ['/5k'], engine)
    assert len(unequip_context.channel.messages) == 1
    assert unequip_context.channel.messages[0] == '/5k is not equipped'
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 900
