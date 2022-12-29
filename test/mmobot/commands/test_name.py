import pytest
from discord import Permissions
from sqlalchemy.orm import Session

from mmobot.commands import name_logic
from mmobot.constants import PERMISSIONS_DEFAULT
from mmobot.db.models.player import Player
from mmobot.test.db import (
    add_player,
    delete_all_entities,
    get_player_with_name,
    init_test_engine
)
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel


engine = init_test_engine()


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture(autouse=True)
def clear_database(session):
    delete_all_entities(session)
    yield
    delete_all_entities(session)


@pytest.fixture
def member():
    return MockMember(100, 'default_name')


@pytest.fixture
def new_members_channel():
    read_write_permissions = Permissions(
        PERMISSIONS_DEFAULT,
        read_messages=True,
        send_messages=True
    )
    return MockTextChannel(1, 'new-players', read_write_permissions)


@pytest.fixture
def town_square_channel():
    channel = MockTextChannel(2, 'town-square')
    return channel


@pytest.fixture
def guild(new_members_channel, town_square_channel):
    guild = MockGuild()
    guild.add_channel(new_members_channel)
    guild.add_channel(town_square_channel)
    return guild


@pytest.fixture
def name_context(member, new_members_channel, guild):
    return MockContext(member, new_members_channel, guild)


@pytest.fixture
def wrong_name_context(member, town_square_channel, guild):
    return MockContext(member, town_square_channel, guild)


@pytest.mark.asyncio
async def test_commandName_newMemberSuccess(name_context, session):
    await name_logic(name_context, ['player'], engine)
    player = get_player_with_name(session, 'player')
    assert player is not None
    assert int(player.discord_id) == 100
    assert player.name == 'player'
    assert player.ancestry == 1
    assert player.is_active is True
    assert player.zone_id == 0
    assert name_context.author.nick == 'player'
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is True
    assert permissions.send_messages is True


@pytest.mark.asyncio
async def test_commandName_withAncestorSuccess(name_context, session):
    player = Player(name='OldPlayer', discord_id=100, ancestry=1, is_active=False)
    add_player(session, player)
    await name_logic(name_context, ['player'], engine)
    player = get_player_with_name(session, 'player')
    assert player is not None
    assert int(player.discord_id) == 100
    assert player.name == 'player'
    assert player.ancestry == 2
    assert player.is_active is True
    assert player.zone_id == 0
    assert name_context.author.nick == 'player'
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is True
    assert permissions.send_messages is True


@pytest.mark.asyncio
async def test_commandName_noArgsProvided(name_context):
    await name_logic(name_context, [], engine)
    assert len(name_context.channel.messages) == 1
    expected_message = 'Please enter the name of your hero! For example: !name Joanne'
    assert name_context.channel.messages[0] == expected_message
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is False
    assert permissions.send_messages is False


@pytest.mark.asyncio
async def test_commandName_wrongChannel(name_context, wrong_name_context):
    await name_logic(wrong_name_context, ['player'], engine)
    assert len(wrong_name_context.channel.messages) == 0
    assert len(name_context.channel.messages) == 0
    assert wrong_name_context.author.nick == 'default_name'
    permissions = wrong_name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is False
    assert permissions.send_messages is False


@pytest.mark.asyncio
async def test_commandName_nameAlreadyTaken(session, name_context):
    player = Player(id=1, name='player', discord_id=99, is_active=True)
    add_player(session, player)
    await name_logic(name_context, ['player'], engine)
    assert len(name_context.channel.messages) == 1
    expected_message = 'Name player has already been taken'
    assert name_context.channel.messages[0] == expected_message
    assert name_context.author.nick == 'default_name'
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is False
    assert permissions.send_messages is False


@pytest.mark.asyncio
async def test_commandName_nameWithSpaces(name_context):
    await name_logic(name_context, ['player', 'with', 'spaces'], engine)
    assert len(name_context.channel.messages) == 1
    expected_message = 'Your name can only be one word, sorry!'
    assert name_context.channel.messages[0] == expected_message
    assert name_context.author.nick == 'default_name'
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is False
    assert permissions.send_messages is False


@pytest.mark.asyncio
async def test_commandName_nameTooShort(name_context):
    await name_logic(name_context, ['x'], engine)
    assert len(name_context.channel.messages) == 1
    expected_message = 'Your name must be between 2 and 20 characters'
    assert name_context.channel.messages[0] == expected_message
    assert name_context.author.nick == 'default_name'
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is False
    assert permissions.send_messages is False


@pytest.mark.asyncio
async def test_commandName_nameTooLong(name_context):
    long_name = 'abcdefghijklmnopqrstuvwxyz'
    await name_logic(name_context, [long_name], engine)
    assert len(name_context.channel.messages) == 1
    expected_message = 'Your name must be between 2 and 20 characters'
    assert name_context.channel.messages[0] == expected_message
    assert name_context.author.nick == 'default_name'
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is False
    assert permissions.send_messages is False


@pytest.mark.asyncio
async def test_commandName_activePlayerExists(name_context):
    # TODO: Implement this edge case later
    pass
