import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mmobot.commands import inventory_logic
from mmobot.db.models.player import Player
from mmobot.test.db import (
    add_item_instance,
    add_player,
    delete_all_entities
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


SINGLE_ITEM_INVENTORY_MESSAGE = '''\
<title>player\'s Inventory</title>
<desc>  0. [ /2 ] : desert-scimitar
</desc>
'''


@pytest.fixture(scope='module')
def engine():
    return create_engine(connection_str)


@pytest.fixture(scope='module')
def session(engine):
    return Session(engine)


@pytest.fixture(autouse=True)
def player(session):
    delete_all_entities(session)
    player = Player(
        id=1,
        name='player',
        discord_id=100,
        is_active=True
    )
    add_player(session, player)
    yield player
    delete_all_entities(session)


@pytest.fixture
def member():
    return MockMember(100, 'player')


@pytest_asyncio.fixture
async def channel(member):
    channel = MockTextChannel(1, 'channel')
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    return channel


@pytest.fixture
def guild(channel):
    guild = MockGuild()
    guild.add_channel(channel)
    return guild


@pytest.fixture
def inventory_context(member, channel, guild):
    return MockContext(member, channel, guild)


@pytest.mark.asyncio
async def test_commandInventory_emptyInventory(inventory_context, engine):
    await inventory_logic(inventory_context, engine)
    assert len(inventory_context.channel.messages) == 1
    expected_message = '<title>player\'s Inventory</title>\n<desc></desc>\n'
    assert inventory_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandInventory_singleItem(inventory_context, engine, session):
    add_item_instance(session, 2, 1, 'desert-scimitar')
    await inventory_logic(inventory_context, engine)
    assert len(inventory_context.channel.messages) == 1
    assert inventory_context.channel.messages[0] == SINGLE_ITEM_INVENTORY_MESSAGE
