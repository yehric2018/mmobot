import pytest
import pytest_asyncio
from sqlalchemy.orm import Session

from mmobot.commands import pickup_logic
from mmobot.db.models.player import Player
from mmobot.db.models.player_stats import PlayerStats
from mmobot.test.db import (
    add_player,
    add_weapon_instance_to_zone,
    delete_all_entities,
    get_item_instance_with_id,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel


MESSAGE_PICKUP_SUCCESS = 'You have picked up: desert-scimitar'


engine = init_test_engine()


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture
def member():
    return MockMember(100, 'player')


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    stats = PlayerStats(hp=100)
    player = Player(id=2222, name='player', discord_id=100, stats=stats, is_active=True)
    add_player(session, player)
    yield
    delete_all_entities(session)


@pytest.fixture()
def setup_item(session, prepare_database):
    add_weapon_instance_to_zone(session, 200, 'town-square', 'desert-scimitar')
    add_weapon_instance_to_zone(session, 201, 'marketplace', 'iron-ore')


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
def pickup_context(member, channel, guild):
    return MockContext(member, channel, guild)


@pytest.mark.asyncio
async def test_commandPickup_withName(pickup_context, session, setup_item):
    await pickup_logic(pickup_context, ['desert-scimitar'], engine)
    assert len(pickup_context.channel.messages) == 1
    assert pickup_context.channel.messages[0] == MESSAGE_PICKUP_SUCCESS
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 2222
    assert item_instance.zone is None


@pytest.mark.asyncio
async def test_commandPickup_withEntityId(pickup_context, session, setup_item):
    await pickup_logic(pickup_context, ['/5k'], engine)
    assert len(pickup_context.channel.messages) == 1
    assert pickup_context.channel.messages[0] == MESSAGE_PICKUP_SUCCESS
    item_instance = get_item_instance_with_id(session, 200)
    assert item_instance.player_id == 2222
    assert item_instance.zone is None


@pytest.mark.asyncio
async def test_commandPickup_incapacitated(pickup_context, session):
    update_player(session, 2222, {'stats.hp': 0})
    await pickup_logic(pickup_context, ['/5k'], engine)
    assert len(pickup_context.channel.messages) == 1
    expected_message = '<@100> You are incapacitated.'
    assert pickup_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandPickup_notInZone(pickup_context, non_zone_channel):
    pickup_context.channel = non_zone_channel
    await pickup_logic(pickup_context, ['desert-scimitar'], engine)
    assert len(pickup_context.channel.messages) == 0


@pytest.mark.asyncio
async def test_commandPickup_noArgsProvided(pickup_context):
    await pickup_logic(pickup_context, [], engine)
    assert len(pickup_context.channel.messages) == 1
    expected_message = 'Please indicate what item you would like to pickup,' \
        ' for example: !pickup item'
    assert pickup_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandPickup_itemNameNotInZone(pickup_context):
    await pickup_logic(pickup_context, ['iron-ore'], engine)
    assert len(pickup_context.channel.messages) == 1
    expected_message = 'Could not find item to pick up: iron-ore'
    assert pickup_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandDrop_entityIdNotInInventory(pickup_context):
    await pickup_logic(pickup_context, ['/5l'], engine)
    assert len(pickup_context.channel.messages) == 1
    expected_message = 'Could not find item to pick up: /5l'
    assert pickup_context.channel.messages[0] == expected_message
