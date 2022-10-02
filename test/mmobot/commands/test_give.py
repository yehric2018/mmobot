import os

import pytest
from dotenv import load_dotenv
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mmobot.commands import give_logic
from mmobot.db.models.player import Player
from mmobot.test.db import (
    add_item_instance,
    add_player,
    delete_all_entities,
    get_item_instance_with_id
)
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel
from mmobot.utils.zones import read_zone_names


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


MESSAGE_GIVE_SUCCESS = '<@101> received desert-scimitar from giver!'
MESSAGE_GIVE_WRONG_USAGE = 'Please supply give arguments like this: **!give player item**'


@pytest.fixture(scope='module')
def engine():
    return create_engine(connection_str)


@pytest.fixture(scope='module')
def session(engine):
    return Session(engine)


@pytest.fixture
def zones():
    return read_zone_names()


@pytest.fixture
def giving_member():
    return MockMember(100, 'giver')


@pytest.fixture
def receiving_member():
    return MockMember(101, 'receiver')


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    add_player(session, Player(id=1, name='giver', discord_id=100, is_active=True))
    add_player(session, Player(id=2, name='receiver', discord_id=101, is_active=True))
    yield
    delete_all_entities(session)


@pytest.fixture()
def setup_item(session, prepare_database):
    add_item_instance(session, 200, 1, 'desert-scimitar')


@pytest_asyncio.fixture
async def channel(giving_member, receiving_member):
    channel = MockTextChannel(1, 'marketplace')
    await channel.set_permissions(giving_member, read_messages=True, send_messages=True)
    await channel.set_permissions(receiving_member, read_messages=True, send_messages=True)
    return channel


@pytest.fixture
def guild(channel):
    guild = MockGuild()
    guild.add_channel(channel)
    return guild


@pytest.fixture
def giving_context(giving_member, channel, guild):
    return MockContext(giving_member, channel, guild)


@pytest.mark.asyncio
async def test_commandGive_withItemName(zones, giving_context, engine, session, setup_item):
    await give_logic(zones, giving_context, ['receiver', 'desert-scimitar'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_SUCCESS
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance is not None
    assert item_instance.id == 200
    assert item_instance.zone_name is None
    assert item_instance.player_id == 2
    assert item_instance.item_id == 'desert-scimitar'


@pytest.mark.asyncio
async def test_commandGive_withInventoryIndex(zones, giving_context, engine, session, setup_item):
    await give_logic(zones, giving_context, ['receiver', '0'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_SUCCESS
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance is not None
    assert item_instance.id == 200
    assert item_instance.zone_name is None
    assert item_instance.player_id == 2
    assert item_instance.item_id == 'desert-scimitar'


@pytest.mark.asyncio
async def test_commandGive_withEntityId(zones, giving_context, engine, session, setup_item):
    await give_logic(zones, giving_context, ['receiver', '/5k'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_SUCCESS
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance is not None
    assert item_instance.id == 200
    assert item_instance.zone_name is None
    assert item_instance.player_id == 2
    assert item_instance.item_id == 'desert-scimitar'


@pytest.mark.asyncio
async def test_commandGive_withDiscordMention(zones, giving_context, engine, session, setup_item):
    await give_logic(zones, giving_context, ['<@101>', 'desert-scimitar'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_SUCCESS
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance is not None
    assert item_instance.id == 200
    assert item_instance.zone_name is None
    assert item_instance.player_id == 2
    assert item_instance.item_id == 'desert-scimitar'


@pytest.mark.asyncio
async def test_commandGive_noArgsProvided(zones, giving_context, engine):
    await give_logic(zones, giving_context, [], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_WRONG_USAGE
    assert giving_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandGive_oneArgProvided(zones, giving_context, engine, session, setup_item):
    await give_logic(zones, giving_context, ['<@101>'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_WRONG_USAGE
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 1


@pytest.mark.asyncio
async def test_commandGive_recieverNotInZone(
        zones, giving_context, receiving_member, engine, session, setup_item):
    await giving_context.channel.set_permissions(
        receiving_member,
        read_messages=False,
        send_messages=False
    )
    await give_logic(zones, giving_context, ['receiver', 'desert-scimitar'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = 'Could not find player receiver in current location'
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 1


@pytest.mark.asyncio
async def test_commandGive_itemNameNotInInventory(
        zones, giving_context, engine, session, setup_item):
    await give_logic(zones, giving_context, ['receiver', 'blazing-blade'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = 'You do not have the item: blazing-blade'
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 1


@pytest.mark.asyncio
async def test_commandGive_inventoryIndexNotInInventory(
        zones, giving_context, engine, session, setup_item):
    await give_logic(zones, giving_context, ['receiver', '200'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = 'You do not have the item: 200'
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 1


@pytest.mark.asyncio
async def test_commandGive_entityIdNotInInventory(
        zones, giving_context, engine, session, setup_item):
    await give_logic(zones, giving_context, ['receiver', '/abc'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = 'You do not have the item: /abc'
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 1
