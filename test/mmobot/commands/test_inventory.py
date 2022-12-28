import pytest
from sqlalchemy.orm import Session

from mmobot.commands import inventory_logic
from mmobot.db.models import FluidContainerInstance, Player
from mmobot.test.constants import (
    TEST_PLAYER_ENTITY_NUMBER,
    TEST_PLAYER_DISCORD_ID,
    TEST_PLAYER_DISCORD_NAME
)
from mmobot.test.db import (
    add_item_instance,
    add_player,
    add_to_database,
    delete_all_entities,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext


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

FLUID_CONTAINERS_MESSAGE = '''\
<title>player\'s Inventory</title>
<desc>  0. [ /2 ] : stone-bowl (water 3/3)
  1. [ /3 ] : stone-bowl (water 2/3)
  2. [ /4 ] : stone-bowl (empty)
</desc>
'''


engine = init_test_engine()


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture(autouse=True)
def player(session):
    delete_all_entities(session)
    player = Player(
        id=TEST_PLAYER_ENTITY_NUMBER,
        name=TEST_PLAYER_DISCORD_NAME,
        discord_id=TEST_PLAYER_DISCORD_ID,
        is_active=True
    )
    add_player(session, player)
    yield player
    delete_all_entities(session)


@pytest.fixture
def inventory_context(member, town_square_channel, test_guild):
    return MockContext(member, town_square_channel, test_guild)


@pytest.mark.asyncio
async def test_commandInventory_emptyInventory(inventory_context):
    await inventory_logic(inventory_context, engine)
    assert len(inventory_context.channel.messages) == 1
    expected_message = '<title>player\'s Inventory</title>\n<desc></desc>\n'
    assert inventory_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandInventory_singleItem(inventory_context, session):
    add_item_instance(session, 2, TEST_PLAYER_ENTITY_NUMBER, 'desert-scimitar')
    await inventory_logic(inventory_context, engine)
    assert len(inventory_context.channel.messages) == 1
    assert inventory_context.channel.messages[0] == SINGLE_ITEM_INVENTORY_MESSAGE


@pytest.mark.asyncio
async def test_commandInventory_equippedWeapon(inventory_context, session):
    add_item_instance(session, 2, TEST_PLAYER_ENTITY_NUMBER, 'desert-scimitar')
    update_player(session, TEST_PLAYER_ENTITY_NUMBER, {'equipped_weapon_id': 2})
    await inventory_logic(inventory_context, engine)
    assert len(inventory_context.channel.messages) == 1
    assert inventory_context.channel.messages[0] == EQUIPPED_WEAPON_INVENTORY_MESSAGE


@pytest.mark.asyncio
async def test_commandInventory_fluidContainers(inventory_context, session):
    fluid_container_full = FluidContainerInstance(
        id=2,
        item_id='stone-bowl',
        owner_id=TEST_PLAYER_ENTITY_NUMBER,
        nonsolid_id='water',
        units=3
    )
    fluid_container_partial = FluidContainerInstance(
        id=3,
        item_id='stone-bowl',
        owner_id=TEST_PLAYER_ENTITY_NUMBER,
        nonsolid_id='water',
        units=2
    )
    fluid_container_empty = FluidContainerInstance(
        id=4,
        item_id='stone-bowl',
        owner_id=TEST_PLAYER_ENTITY_NUMBER,
        nonsolid_id=None,
        units=0
    )
    add_to_database(session, fluid_container_full)
    add_to_database(session, fluid_container_partial)
    add_to_database(session, fluid_container_empty)

    await inventory_logic(inventory_context, engine)
    assert len(inventory_context.channel.messages) == 1
    assert inventory_context.channel.messages[0] == FLUID_CONTAINERS_MESSAGE


@pytest.mark.asyncio
async def test_commandInventory_notInZone(inventory_context, non_zone_channel):
    inventory_context.channel = non_zone_channel
    await inventory_logic(inventory_context, engine)
    assert len(inventory_context.channel.messages) == 0
