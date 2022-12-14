import pytest
import pytest_asyncio

from mmobot.test.constants import (
    TEST_CHANNEL_MARKETPLACE_ID,
    TEST_CHANNEL_MARKETPLACE_NAME,
    TEST_CHANNEL_TOWN_SQUARE_NAME,
    TEST_CHANNEL_TOWN_SQUARE_ID,
    TEST_PLAYER_DISCORD_ID_2,
    TEST_PLAYER_DISCORD_NAME_2
)
from mmobot.test.mock import MockGuild, MockMember, MockTextChannel


@pytest.fixture
def member():
    return MockMember(100, 'player')


@pytest.fixture
def member_2():
    return MockMember(TEST_PLAYER_DISCORD_ID_2, TEST_PLAYER_DISCORD_NAME_2)


@pytest_asyncio.fixture
async def town_square_channel(member, member_2):
    channel = MockTextChannel(
        TEST_CHANNEL_TOWN_SQUARE_ID,
        TEST_CHANNEL_TOWN_SQUARE_NAME,
        category='World'
    )
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    await channel.set_permissions(member_2, read_messages=True, send_messages=True)
    return channel


@pytest_asyncio.fixture
async def marketplace_channel():
    return MockTextChannel(
        TEST_CHANNEL_MARKETPLACE_ID,
        TEST_CHANNEL_MARKETPLACE_NAME,
        category='World'
    )


@pytest_asyncio.fixture
async def non_zone_channel():
    return MockTextChannel(2, 'general')


@pytest.fixture
def test_guild(town_square_channel, non_zone_channel):
    guild = MockGuild()
    guild.add_channel(town_square_channel)
    guild.add_channel(non_zone_channel)
    return guild
