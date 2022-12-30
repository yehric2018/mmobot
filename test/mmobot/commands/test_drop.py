import pytest
from sqlalchemy.orm import Session

from mmobot.commands import drop_logic
from mmobot.test.constants import (
    TEST_IRON_SWORD_WEIGHT,
    TEST_PLAYER_ENTITY_NUMBER,
    TEST_PLAYER_DISCORD_NAME,
    TEST_PLAYER_DISCORD_ID,
    TEST_TOWN_SQUARE_ZONE_ID
)
from mmobot.db.models.player import Player
from mmobot.test.db import (
    add_player,
    add_weapon_instance,
    delete_all_entities,
    get_item_instance_with_id,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext


MESSAGE_DROP_SUCCESS = 'You have dropped: iron-sword'


engine = init_test_engine()


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    player = Player(
        id=TEST_PLAYER_ENTITY_NUMBER,
        name=TEST_PLAYER_DISCORD_NAME,
        discord_id=TEST_PLAYER_DISCORD_ID,
        is_active=True,
        zone_id=TEST_TOWN_SQUARE_ZONE_ID,
        inventory_weight=TEST_IRON_SWORD_WEIGHT
    )
    add_player(session, player)
    yield
    delete_all_entities(session)


@pytest.fixture()
def setup_item(session, prepare_database):
    add_weapon_instance(session, 200, TEST_PLAYER_ENTITY_NUMBER, 'iron-sword')


@pytest.fixture
def drop_context(member, town_square_channel, test_guild):
    return MockContext(member, town_square_channel, test_guild)


@pytest.mark.asyncio
async def test_commandDrop_withName(drop_context, session, setup_item):
    await drop_logic(drop_context, ['iron-sword'], engine)
    assert len(drop_context.channel.messages) == 1
    assert drop_context.channel.messages[0] == MESSAGE_DROP_SUCCESS
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.owner_id is None
    assert item_instance.zone_id == TEST_TOWN_SQUARE_ZONE_ID
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.inventory_weight == 0


@pytest.mark.asyncio
async def test_commandDrop_withInventoryIndex(drop_context, session, setup_item):
    await drop_logic(drop_context, ['0'], engine)
    assert len(drop_context.channel.messages) == 1
    assert drop_context.channel.messages[0] == MESSAGE_DROP_SUCCESS
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.owner_id is None
    assert item_instance.zone_id == TEST_TOWN_SQUARE_ZONE_ID
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.inventory_weight == 0


@pytest.mark.asyncio
async def test_commandDrop_withEntityId(drop_context, session, setup_item):
    await drop_logic(drop_context, ['/5k'], engine)
    assert len(drop_context.channel.messages) == 1
    assert drop_context.channel.messages[0] == MESSAGE_DROP_SUCCESS
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.owner_id is None
    assert item_instance.zone_id == TEST_TOWN_SQUARE_ZONE_ID
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.inventory_weight == 0


@pytest.mark.asyncio
async def test_commandDrop_dropEquippedWeapon(drop_context, session, setup_item):
    update_player(session, 2222, {
        'equipped_weapon_id': 200,
        'inventory_weight': TEST_IRON_SWORD_WEIGHT * 2
    })
    await drop_logic(drop_context, ['iron-sword'], engine)
    assert len(drop_context.channel.messages) == 1
    assert drop_context.channel.messages[0] == MESSAGE_DROP_SUCCESS
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.owner_id is None
    assert item_instance.zone_id == TEST_TOWN_SQUARE_ZONE_ID
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id is None
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.inventory_weight == 0


@pytest.mark.asyncio
async def test_commandDrop_notInZone(drop_context, non_zone_channel):
    drop_context.channel = non_zone_channel
    await drop_logic(drop_context, ['iron-sword'], engine)
    assert len(drop_context.channel.messages) == 0


@pytest.mark.asyncio
async def test_commandDrop_noArgsProvided(drop_context):
    await drop_logic(drop_context, [], engine)
    assert len(drop_context.channel.messages) == 1
    expected_message = 'Please indicate what item you would like to drop,' \
        ' for example: !drop item'
    assert drop_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandDrop_itemNameNotInInventory(drop_context, session):
    await drop_logic(drop_context, ['desert-scimitar'], engine)
    assert len(drop_context.channel.messages) == 1
    expected_message = 'You do not have the item: desert-scimitar'
    assert drop_context.channel.messages[0] == expected_message
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.inventory_weight == TEST_IRON_SWORD_WEIGHT


@pytest.mark.asyncio
async def test_commandDrop_inventoryIndexNotInInventory(drop_context, session):
    await drop_logic(drop_context, ['77'], engine)
    assert len(drop_context.channel.messages) == 1
    expected_message = 'You do not have the item: 77'
    assert drop_context.channel.messages[0] == expected_message
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.inventory_weight == TEST_IRON_SWORD_WEIGHT


@pytest.mark.asyncio
async def test_commandDrop_entityIdNotInInventory(drop_context, session):
    await drop_logic(drop_context, ['/zzzzz'], engine)
    assert len(drop_context.channel.messages) == 1
    expected_message = 'You do not have the item: /zzzzz'
    assert drop_context.channel.messages[0] == expected_message
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.inventory_weight == TEST_IRON_SWORD_WEIGHT
