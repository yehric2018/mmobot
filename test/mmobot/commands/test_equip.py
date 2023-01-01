import pytest
from sqlalchemy.orm import Session

from mmobot.commands import equip_logic
from mmobot.db.models import ArrowInstance, BowInstance, ItemInstance, Player
from mmobot.test.constants import MESSAGE_TEST_PLAYER_INCAPACITATED
from mmobot.test.db import (
    add_player,
    add_to_database,
    add_weapon_instance,
    delete_all_entities,
    get_item_instance_with_id,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext


MESSAGE_EQUIP_SUCCESS = '<@100> You have equipped: [ /5k ] desert-scimitar'
MESSAGE_EQUIP_PICKAXE_SUCCESS = '<@100> You have equipped: [ /5l ] basic-pickaxe'
MESSAGE_BOW_NOT_EQUIPPED = '<@100> You must have a bow equipped first.'
MESSAGE_EQUIP_BOW_SUCCESS = '<@100> You have equipped: [ /5p ] wooden-bow'
MESSAGE_EQUIP_ARROW_SUCCESS = '<@100> You have equipped: [ /5m ] stonehead-arrow'


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
    add_to_database(session, BowInstance(id=205, owner_id=1, item_id='wooden-bow'))
    add_to_database(session, ArrowInstance(id=202, owner_id=1, item_id='stonehead-arrow'))
    add_to_database(session, ItemInstance(id=208, owner_id=1, item_id='knights-armor'))
    add_to_database(session, ItemInstance(id=209, owner_id=1, item_id='stone'))


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
    expected_message = '<@100> You have equipped: [ /5s ] knights-armor'
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
    expected_message = '<@100> Please indicate what item you would like to equip,' \
        ' for example: !equip item'
    assert equip_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEquip_itemNameNotInInventory(equip_context):
    await equip_logic(equip_context, ['iron-sword'], engine)
    assert len(equip_context.channel.messages) == 1
    expected_message = '<@100> You do not have the item: iron-sword'
    assert equip_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEquip_entityIdNotInInventory(equip_context):
    await equip_logic(equip_context, ['/abc'], engine)
    assert len(equip_context.channel.messages) == 1
    expected_message = '<@100> You do not have the item: /abc'
    assert equip_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEquip_itemNotEquippable(equip_context, session, setup_item):
    # TODO: Add some nonequippable items and write this test (most likely iron/ore)
    await equip_logic(equip_context, ['/5t'], engine)
    assert len(equip_context.channel.messages) == 1
    expected_message = '<@100> [ /5t ] stone cannot be equipped'
    assert equip_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEquip_equipArrowNothingEquipped(equip_context, session, setup_item):
    await equip_logic(equip_context, ['stonehead-arrow'], engine)
    assert len(equip_context.channel.messages) == 1
    assert equip_context.channel.messages[0] == MESSAGE_BOW_NOT_EQUIPPED
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id is None


@pytest.mark.asyncio
async def test_commandEquip_equipArrowWeaponEquipped(equip_context, session, setup_item):
    await equip_logic(equip_context, ['desert-scimitar'], engine)
    await equip_logic(equip_context, ['stonehead-arrow'], engine)
    assert len(equip_context.channel.messages) == 2
    assert equip_context.channel.messages[1] == MESSAGE_BOW_NOT_EQUIPPED
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 200


@pytest.mark.asyncio
async def test_commandEquip_equipArrowWithBow(equip_context, session, setup_item):
    await equip_logic(equip_context, ['wooden-bow'], engine)
    await equip_logic(equip_context, ['stonehead-arrow'], engine)
    assert len(equip_context.channel.messages) == 2
    assert equip_context.channel.messages[0] == MESSAGE_EQUIP_BOW_SUCCESS
    assert equip_context.channel.messages[1] == MESSAGE_EQUIP_ARROW_SUCCESS
    player = get_player_with_name(session, 'player')
    assert player.equipped_weapon_id == 205
    item_instance = get_item_instance_with_id(session, 205)
    assert item_instance.owner_id == 1
    assert isinstance(item_instance, BowInstance)
    assert item_instance.arrow_id == 202
