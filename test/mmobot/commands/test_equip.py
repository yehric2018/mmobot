import pytest
from sqlalchemy.orm import Session

from mmobot.commands import equip_logic
from mmobot.db.models import Player
from mmobot.test.constants import MESSAGE_TEST_PLAYER_INCAPACITATED
from mmobot.test.db import (
    add_player,
    add_weapon_instance,
    delete_all_entities,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext


MESSAGE_EQUIP_SUCCESS = 'You have equipped: desert-scimitar'
MESSAGE_EQUIP_PICKAXE_SUCCESS = 'You have equipped: basic-pickaxe'


engine = init_test_engine()


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    add_player(session, Player(id=1, name='player', discord_id=100, hp=100, is_active=True))
    yield
    delete_all_entities(session)


@pytest.fixture()
def setup_item(session, prepare_database):
    add_weapon_instance(session, 200, 1, 'desert-scimitar')
    add_weapon_instance(session, 208, 1, 'knights-armor')


@pytest.fixture
def equip_context(member, town_square_channel, test_guild):
    return MockContext(member, town_square_channel, test_guild)


@pytest.mark.asyncio
async def test_commandEquip_weaponWithName(equip_context, session, setup_item):
    await equip_logic(equip_context, ['desert-scimitar'], engine)
    assert len(equip_context.channel.messages) == 1
    assert equip_context.channel.messages[0] == MESSAGE_EQUIP_SUCCESS
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 200


@pytest.mark.asyncio
async def test_commandEquip_weaponWithInventoryIndex(equip_context, session, setup_item):
    await equip_logic(equip_context, ['0'], engine)
    assert len(equip_context.channel.messages) == 1
    assert equip_context.channel.messages[0] == MESSAGE_EQUIP_SUCCESS
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 200


@pytest.mark.asyncio
async def test_commandEquip_weaponWithEntityId(equip_context, session, setup_item):
    await equip_logic(equip_context, ['/5k'], engine)
    assert len(equip_context.channel.messages) == 1
    assert equip_context.channel.messages[0] == MESSAGE_EQUIP_SUCCESS
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 200


@pytest.mark.asyncio
async def test_commandEquip_attireWithEntityId(equip_context, session, setup_item):
    await equip_logic(equip_context, ['/5s'], engine)
    assert len(equip_context.channel.messages) == 1
    expected_message = 'You have equipped: knights-armor'
    assert equip_context.channel.messages[0] == expected_message
    player = get_player_with_name(session, 'player')
    assert player.equipped_attire_id == 208


@pytest.mark.asyncio
async def test_commandEquip_replaceOldWeapon(equip_context, session, setup_item):
    add_weapon_instance(session, 201, 1, 'basic-pickaxe')
    await equip_logic(equip_context, ['desert-scimitar'], engine)
    await equip_logic(equip_context, ['basic-pickaxe'], engine)
    assert len(equip_context.channel.messages) == 2
    assert equip_context.channel.messages[0] == MESSAGE_EQUIP_SUCCESS
    assert equip_context.channel.messages[1] == MESSAGE_EQUIP_PICKAXE_SUCCESS
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 201


@pytest.mark.asyncio
async def test_commandEquip_notInZone(
        equip_context, non_zone_channel, setup_item):
    equip_context.channel = non_zone_channel
    await equip_logic(equip_context, ['desert-scimitar'], engine)
    assert len(equip_context.channel.messages) == 0


@pytest.mark.asyncio
async def test_commandEquip_incapacitated(equip_context, session):
    update_player(session, 1, {'hp': 0})
    await equip_logic(equip_context, ['desert-scimitar'], engine)
    assert len(equip_context.channel.messages) == 1
    expected_message = MESSAGE_TEST_PLAYER_INCAPACITATED
    assert equip_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEquip_noArgsProvided(equip_context):
    await equip_logic(equip_context, [], engine)
    assert len(equip_context.channel.messages) == 1
    expected_message = 'Please indicate what item you would like to equip,' \
        ' for example: !equip item'
    assert equip_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEquip_itemNameNotInInventory(equip_context):
    await equip_logic(equip_context, ['iron-sword'], engine)
    assert len(equip_context.channel.messages) == 1
    expected_message = 'You do not have the item: iron-sword'
    assert equip_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEquip_inventoryIndexNotInInventory(equip_context):
    await equip_logic(equip_context, ['20'], engine)
    assert len(equip_context.channel.messages) == 1
    expected_message = 'You do not have the item: 20'
    assert equip_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEquip_entityIdNotInInventory(equip_context):
    await equip_logic(equip_context, ['/abc'], engine)
    assert len(equip_context.channel.messages) == 1
    expected_message = 'You do not have the item: /abc'
    assert equip_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEquip_itemNotEquippable():
    # TODO: Add some nonequippable items and write this test (most likely iron/ore)
    pass
