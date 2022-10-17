import pytest
import pytest_asyncio

from mmobot.commands import navigation_logic
from mmobot.test.db import init_test_engine
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel


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
<field>Minizones:0. bell-tower
</field>
'''


engine = init_test_engine()


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
async def test_commandNavigation_success(navigation_context):
    await navigation_logic(navigation_context, engine)
    assert len(navigation_context.channel.messages) == 1
    assert navigation_context.channel.messages[0] == REACHABLE_FROM_TOWN_SQUARE_MESSAGE


@pytest.mark.asyncio
async def test_commandNavigation_notInZoneChannel(navigation_context, non_zone_channel):
    navigation_context.channel = non_zone_channel
    await navigation_logic(navigation_context, engine)
    assert len(navigation_context.channel.messages) == 0
