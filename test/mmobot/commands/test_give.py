import pytest
import pytest_asyncio
from sqlalchemy.orm import Session

from mmobot.commands import give_logic
from mmobot.db.models.player import Player
from mmobot.test.db import (
    add_item_instance,
    add_player,
    delete_all_entities,
    get_item_instance_with_id,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel


MESSAGE_GIVE_SUCCESS = '<@101> received desert-scimitar from giver!'
MESSAGE_GIVE_WRONG_USAGE = 'Please supply give arguments like this: **!give player item**'


engine = init_test_engine()


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture
def giving_member():
    return MockMember(100, 'giver')


@pytest.fixture
def receiving_member():
    return MockMember(101, 'receiver')


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    add_player(session, Player(
        id=1,
        name='giver',
        discord_id=100,
        is_active=True,
        zone='marketplace'
    ))
    add_player(session, Player(
        id=2,
        name='receiver',
        discord_id=101,
        is_active=True,
        zone='marketplace'
    ))
    yield
    delete_all_entities(session)


@pytest.fixture()
def setup_item(session, prepare_database):
    add_item_instance(session, 200, 1, 'desert-scimitar')


@pytest_asyncio.fixture
async def channel(giving_member, receiving_member):
    channel = MockTextChannel(1, 'marketplace', category='World')
    await channel.set_permissions(giving_member, read_messages=True, send_messages=True)
    await channel.set_permissions(receiving_member, read_messages=True, send_messages=True)
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
def giving_context(giving_member, channel, guild):
    return MockContext(giving_member, channel, guild)


@pytest.mark.asyncio
async def test_commandGive_withItemName(giving_context, session, setup_item):
    await give_logic(giving_context, ['receiver', 'desert-scimitar'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_SUCCESS
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance is not None
    assert item_instance.id == 200
    assert item_instance.zone is None
    assert item_instance.player_id == 2
    assert item_instance.item_id == 'desert-scimitar'


@pytest.mark.asyncio
async def test_commandGive_withInventoryIndex(giving_context, session, setup_item):
    await give_logic(giving_context, ['receiver', '0'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_SUCCESS
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance is not None
    assert item_instance.id == 200
    assert item_instance.zone is None
    assert item_instance.player_id == 2
    assert item_instance.item_id == 'desert-scimitar'


@pytest.mark.asyncio
async def test_commandGive_withEntityId(giving_context, session, setup_item):
    await give_logic(giving_context, ['receiver', '/5k'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_SUCCESS
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance is not None
    assert item_instance.id == 200
    assert item_instance.zone is None
    assert item_instance.player_id == 2
    assert item_instance.item_id == 'desert-scimitar'


@pytest.mark.asyncio
async def test_commandGive_withDiscordMention(giving_context, session, setup_item):
    await give_logic(giving_context, ['<@101>', 'desert-scimitar'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_SUCCESS
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance is not None
    assert item_instance.id == 200
    assert item_instance.zone is None
    assert item_instance.player_id == 2
    assert item_instance.item_id == 'desert-scimitar'


@pytest.mark.asyncio
async def test_commandGive_equippedWeapon(giving_context, session, setup_item):
    update_player(session, 1, {'equipped_weapon_id': 200})
    await give_logic(giving_context, ['receiver', 'desert-scimitar'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_SUCCESS
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance is not None
    assert item_instance.id == 200
    assert item_instance.zone is None
    assert item_instance.player_id == 2
    assert item_instance.item_id == 'desert-scimitar'
    player = get_player_with_name(session, 'giver')
    assert player.equipped_weapon_id is None


@pytest.mark.asyncio
async def test_commandGive_noArgsProvided(giving_context):
    await give_logic(giving_context, [], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_WRONG_USAGE
    assert giving_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandGive_oneArgProvided(giving_context, session, setup_item):
    await give_logic(giving_context, ['<@101>'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = MESSAGE_GIVE_WRONG_USAGE
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 1


@pytest.mark.asyncio
async def test_commandGive_notInZone(
        giving_context, non_zone_channel, setup_item):
    giving_context.channel = non_zone_channel
    await give_logic(giving_context, ['receiver', 'desert-scimitar'], engine)
    assert len(giving_context.channel.messages) == 0


@pytest.mark.asyncio
async def test_commandGive_recieverNotInZone(
        giving_context, receiving_member, session, setup_item):
    await giving_context.channel.set_permissions(
        receiving_member,
        read_messages=False,
        send_messages=False
    )
    update_player(session, 2, {'zone': 'town-square'})
    await give_logic(giving_context, ['receiver', 'desert-scimitar'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = 'Could not find player receiver in current location'
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 1


@pytest.mark.asyncio
async def test_commandGive_itemNameNotInInventory(giving_context, session, setup_item):
    await give_logic(giving_context, ['receiver', 'blazing-blade'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = 'You do not have the item: blazing-blade'
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 1


@pytest.mark.asyncio
async def test_commandGive_inventoryIndexNotInInventory(giving_context, session, setup_item):
    await give_logic(giving_context, ['receiver', '200'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = 'You do not have the item: 200'
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 1


@pytest.mark.asyncio
async def test_commandGive_entityIdNotInInventory(giving_context, session, setup_item):
    await give_logic(giving_context, ['receiver', '/abc'], engine)
    assert len(giving_context.channel.messages) == 1
    expected_message = 'You do not have the item: /abc'
    assert giving_context.channel.messages[0] == expected_message
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 1
