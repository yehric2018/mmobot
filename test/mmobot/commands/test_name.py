import os

import pytest
from discord import Permissions
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mmobot.commands import name_logic
from mmobot.constants import PERMISSIONS_DEFAULT
from mmobot.db.models.player import Player
from mmobot.test.db import (
    add_player,
    delete_all_entities,
    get_player_with_name
)
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel


load_dotenv()
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_DATABASE_NAME = os.getenv('MYSQL_TEST_DATABASE_NAME')

connection_str = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
    MYSQL_USERNAME,
    MYSQL_PASSWORD,
    MYSQL_HOSTNAME,
    MYSQL_DATABASE_NAME
)


@pytest.fixture(scope='module')
def engine():
    return create_engine(connection_str)


@pytest.fixture(scope='module')
def session(engine):
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
async def test_commandName_newMemberSuccess(name_context, engine, session):
    await name_logic(name_context, ['player'], engine)
    player = get_player_with_name(session, 'player')
    assert player is not None
    assert int(player.discord_id) == 100
    assert player.name == 'player'
    assert player.ancestry == 1
    assert player.is_active is True
    assert name_context.author.nick == 'player'
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is True
    assert permissions.send_messages is True


@pytest.mark.asyncio
async def test_commandName_withAncestorSuccess(name_context, engine, session):
    player = Player(name='OldPlayer', discord_id=100, ancestry=1, is_active=False)
    add_player(session, player)
    await name_logic(name_context, ['player'], engine)
    player = get_player_with_name(session, 'player')
    assert player is not None
    assert int(player.discord_id) == 100
    assert player.name == 'player'
    assert player.ancestry == 2
    assert player.is_active is True
    assert name_context.author.nick == 'player'
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is True
    assert permissions.send_messages is True


@pytest.mark.asyncio
async def test_commandName_noArgsProvided(name_context, engine):
    await name_logic(name_context, [], engine)
    assert len(name_context.channel.messages) == 1
    expected_message = 'Please enter the name of your hero! For example: !name Joanne'
    assert name_context.channel.messages[0] == expected_message
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is False
    assert permissions.send_messages is False


@pytest.mark.asyncio
async def test_commandName_wrongChannel(name_context, engine, wrong_name_context):
    await name_logic(wrong_name_context, ['player'], engine)
    assert len(wrong_name_context.channel.messages) == 0
    assert len(name_context.channel.messages) == 0
    assert wrong_name_context.author.nick == 'default_name'
    permissions = wrong_name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is False
    assert permissions.send_messages is False


@pytest.mark.asyncio
async def test_commandName_nameAlreadyTaken(session, name_context, engine):
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
async def test_commandName_nameWithSpaces(name_context, engine):
    await name_logic(name_context, ['player', 'with', 'spaces'], engine)
    assert len(name_context.channel.messages) == 1
    expected_message = 'Your name can only be one word, sorry!'
    assert name_context.channel.messages[0] == expected_message
    assert name_context.author.nick == 'default_name'
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is False
    assert permissions.send_messages is False


@pytest.mark.asyncio
async def test_commandName_nameTooShort(name_context, engine):
    await name_logic(name_context, ['x'], engine)
    assert len(name_context.channel.messages) == 1
    expected_message = 'Your name must be between 2 and 20 characters'
    assert name_context.channel.messages[0] == expected_message
    assert name_context.author.nick == 'default_name'
    permissions = name_context.guild.channels[1].permissions_for(name_context.author)
    assert permissions.read_messages is False
    assert permissions.send_messages is False


@pytest.mark.asyncio
async def test_commandName_nameTooLong(name_context, engine):
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
async def test_commandName_activePlayerExists(name_context, engine):
    # TODO: Implement this edge case later
    pass
