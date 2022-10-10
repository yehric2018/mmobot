import os

import pytest
from dotenv import load_dotenv
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mmobot.commands import drop_logic
from mmobot.db.models.player import Player
from mmobot.test.db import (
    add_player,
    add_weapon_instance,
    delete_all_entities,
    get_item_instance_with_id,
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


MESSAGE_DROP_SUCCESS = 'You have dropped: desert-scimitar'


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
    add_player(session, Player(id=2222, name='player', discord_id=100, is_active=True))
    yield
    delete_all_entities(session)


@pytest.fixture()
def setup_item(session, prepare_database):
    add_weapon_instance(session, 200, 2222, 'desert-scimitar')


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
def drop_context(member, channel, guild):
    return MockContext(member, channel, guild)


@pytest.mark.asyncio
async def test_commandDrop_withName(drop_context, engine, session, setup_item):
    await drop_logic(drop_context, ['desert-scimitar'], engine)
    assert len(drop_context.channel.messages) == 1
    assert drop_context.channel.messages[0] == MESSAGE_DROP_SUCCESS
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id is None
    assert item_instance.zone == 'town-square'


@pytest.mark.asyncio
async def test_commandDrop_withInventoryIndex(drop_context, engine, session, setup_item):
    await drop_logic(drop_context, ['0'], engine)
    assert len(drop_context.channel.messages) == 1
    assert drop_context.channel.messages[0] == MESSAGE_DROP_SUCCESS
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id is None
    assert item_instance.zone == 'town-square'


@pytest.mark.asyncio
async def test_commandDrop_withEntityId(drop_context, engine, session, setup_item):
    await drop_logic(drop_context, ['/5k'], engine)
    assert len(drop_context.channel.messages) == 1
    assert drop_context.channel.messages[0] == MESSAGE_DROP_SUCCESS
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id is None
    assert item_instance.zone == 'town-square'


@pytest.mark.asyncio
async def test_commandDrop_dropEquippedWeapon(drop_context, engine, session, setup_item):
    update_player(session, 2222, {'equipped_weapon_id': 200})
    await drop_logic(drop_context, ['desert-scimitar'], engine)
    assert len(drop_context.channel.messages) == 1
    assert drop_context.channel.messages[0] == MESSAGE_DROP_SUCCESS
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id is None
    assert item_instance.zone == 'town-square'
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id is None


@pytest.mark.asyncio
async def test_commandDrop_notInZone(drop_context, non_zone_channel, engine):
    drop_context.channel = non_zone_channel
    await drop_logic(drop_context, ['desert-scimitar'], engine)
    assert len(drop_context.channel.messages) == 0


@pytest.mark.asyncio
async def test_commandDrop_noArgsProvided(drop_context, engine):
    await drop_logic(drop_context, [], engine)
    assert len(drop_context.channel.messages) == 1
    expected_message = 'Please indicate what item you would like to drop,' \
        ' for example: !drop item'
    assert drop_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandDrop_itemNameNotInInventory(drop_context, engine):
    await drop_logic(drop_context, ['iron-sword'], engine)
    assert len(drop_context.channel.messages) == 1
    expected_message = 'You do not have the item: iron-sword'
    assert drop_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandDrop_inventoryIndexNotInInventory(drop_context, engine):
    await drop_logic(drop_context, ['77'], engine)
    assert len(drop_context.channel.messages) == 1
    expected_message = 'You do not have the item: 77'
    assert drop_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandDrop_entityIdNotInInventory(drop_context, engine):
    await drop_logic(drop_context, ['/zzzzz'], engine)
    assert len(drop_context.channel.messages) == 1
    expected_message = 'You do not have the item: /zzzzz'
    assert drop_context.channel.messages[0] == expected_message
