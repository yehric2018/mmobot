import pytest
import pytest_asyncio

from mmobot.test.mock import MockGuild, MockMember, MockTextChannel


@pytest.fixture
def member():
    return MockMember(100, 'player')


@pytest_asyncio.fixture
async def town_square_channel(member):
    channel = MockTextChannel(1, 'town-square', category='World')
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    return channel


@pytest_asyncio.fixture
async def non_zone_channel():
    return MockTextChannel(2, 'general')


@pytest.fixture
def test_guild(town_square_channel, non_zone_channel):
    guild = MockGuild()
    guild.add_channel(town_square_channel)
    guild.add_channel(non_zone_channel)
    return guild