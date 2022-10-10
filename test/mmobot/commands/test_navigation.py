import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine

from mmobot.commands import navigation_logic
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


REACHABLE_FROM_TOWN_SQUARE_MESSAGE = '''\
<title>You can reach the following locations from town-square:</title>
<desc>0. arena
1. barracks
2. city-gate
3. marketplace
4. mines-entrance
5. royal-palace
6. tavern
7. yak-farm
</desc>
'''


@pytest.fixture
def engine():
    return create_engine(connection_str)


@pytest.fixture
def zones():
    return read_zone_names()


@pytest.fixture
def member():
    return MockMember(1, 'member')


@pytest_asyncio.fixture
async def zone_channel(member):
    channel = MockTextChannel(11, 'town-square', category='World')
    await channel.set_permissions(
        member,
        read_messages=True,
        send_messages=False
    )
    return channel


@pytest.fixture
def non_zone_channel():
    return MockTextChannel(13, 'general')


@pytest.fixture
def guild(zone_channel, non_zone_channel):
    guild = MockGuild()
    guild.add_channel(zone_channel)
    guild.add_channel(non_zone_channel)
    return guild


@pytest.fixture
def navigation_context(member, zone_channel, guild):
    return MockContext(member, zone_channel, guild)


@pytest.mark.asyncio
async def test_commandNavigation_success(zones, navigation_context, engine):
    await navigation_logic(zones, navigation_context, engine)
    assert len(navigation_context.channel.messages) == 1
    assert navigation_context.channel.messages[0] == REACHABLE_FROM_TOWN_SQUARE_MESSAGE


@pytest.mark.asyncio
async def test_commandNavigation_notInZoneChannel(
        zones, navigation_context, non_zone_channel, engine):
    navigation_context.channel = non_zone_channel
    await navigation_logic(zones, navigation_context, engine)
    assert len(navigation_context.channel.messages) == 0
