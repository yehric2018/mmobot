import pytest

from mmobot.commands import navigation_logic
from mmobot.test.db import init_test_engine
from mmobot.test.mock import MockContext


REACHABLE_FROM_TOWN_SQUARE_MESSAGE = '''\
<title>You can reach the following locations from town-square:</title>
<desc>None</desc>
<field>:arrow_left: West:marketplace</field>
<field>:arrow_up: North:barracks</field>
<field>:arrow_right: East:mines-entrance</field>
'''


engine = init_test_engine()


@pytest.fixture
def navigation_context(member, town_square_channel, test_guild):
    return MockContext(member, town_square_channel, test_guild)


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
