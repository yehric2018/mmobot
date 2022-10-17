import pytest
import pytest_asyncio
from sqlalchemy.orm import Session

from mmobot.commands import inventory_logic
from mmobot.db.models.player import Player
from mmobot.test.db import (
    add_item_instance,
    add_player,
    delete_all_entities,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel


SINGLE_ITEM_INVENTORY_MESSAGE = '''\
<title>player\'s Inventory</title>
<desc>  0. [ /2 ] : desert-scimitar
</desc>
'''

EQUIPPED_WEAPON_INVENTORY_MESSAGE = '''\
<title>player\'s Inventory</title>
<desc>  0. [ /2 ] : desert-scimitar **(weapon)**
</desc>
'''


engine = init_test_engine()


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture(autouse=True)
def player(session):
    delete_all_entities(session)
    player = Player(id=1, name='player', discord_id=100, is_active=True)
    add_player(session, player)
    yield player
    delete_all_entities(session)


@pytest.fixture
def member():
    return MockMember(100, 'player')


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
def inventory_context(member, channel, guild):
    return MockContext(member, channel, guild)


@pytest.mark.asyncio
async def test_commandInventory_emptyInventory(inventory_context):
    await inventory_logic(inventory_context, engine)
    assert len(inventory_context.channel.messages) == 1
    expected_message = '<title>player\'s Inventory</title>\n<desc></desc>\n'
    assert inventory_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandInventory_singleItem(inventory_context, session):
    add_item_instance(session, 2, 1, 'desert-scimitar')
    await inventory_logic(inventory_context, engine)
    assert len(inventory_context.channel.messages) == 1
    assert inventory_context.channel.messages[0] == SINGLE_ITEM_INVENTORY_MESSAGE


@pytest.mark.asyncio
async def test_commandInventory_equippedWeapon(inventory_context, session):
    add_item_instance(session, 2, 1, 'desert-scimitar')
    update_player(session, 1, {'equipped_weapon_id': 2})
    await inventory_logic(inventory_context, engine)
    assert len(inventory_context.channel.messages) == 1
    assert inventory_context.channel.messages[0] == EQUIPPED_WEAPON_INVENTORY_MESSAGE


@pytest.mark.asyncio
async def test_commandInventory_notInZone(inventory_context, non_zone_channel):
    inventory_context.channel = non_zone_channel
    await inventory_logic(inventory_context, engine)
    assert len(inventory_context.channel.messages) == 0
