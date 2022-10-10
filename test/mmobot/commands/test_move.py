import os
from discord import Permissions

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine

from mmobot.commands import move_logic
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


DEFAULT_PERMISSIONS = 0


@pytest.fixture
def engine():
    return create_engine(connection_str)


@pytest.fixture
def moving_member():
    return MockMember(1, 'member')


@pytest.fixture
def no_permissions():
    return Permissions(DEFAULT_PERMISSIONS)


@pytest.fixture
def read_write_permissions():
    return Permissions(DEFAULT_PERMISSIONS, read_messages=True, send_messages=True)


@pytest_asyncio.fixture
async def current_channel(moving_member):
    channel = MockTextChannel(11, 'town-square', category='World')
    await channel.set_permissions(
        moving_member,
        read_messages=True,
        send_messages=False
    )
    return channel


@pytest.fixture
def destination_channel():
    return MockTextChannel(12, 'marketplace', category='World')


@pytest.fixture
def non_zone_channel():
    return MockTextChannel(13, 'general')


@pytest.fixture
def guild(current_channel, destination_channel, non_zone_channel):
    guild = MockGuild()
    guild.add_channel(current_channel)
    guild.add_channel(destination_channel)
    guild.add_channel(non_zone_channel)
    return guild


@pytest.fixture
def move_context(moving_member, current_channel, guild):
    return MockContext(moving_member, current_channel, guild)


@pytest.mark.asyncio
async def test_commandMove_success(
        move_context, moving_member, engine, no_permissions, read_write_permissions):
    await move_logic(move_context, ['marketplace'], engine)

    assert len(move_context.channel.messages) == 1
    leaving_message = '<@1> has left for <#12>.'
    assert move_context.channel.messages[0] == leaving_message

    assert len(move_context.guild.channels[1].messages) == 1
    entering_message = '<@1> has arrived.'
    assert move_context.guild.channels[1].messages[0] == entering_message

    leaving_permissions = move_context.channel.permissions_for(moving_member)
    assert leaving_permissions == no_permissions
    entering_permissions = move_context.guild.channels[1].permissions_for(moving_member)
    assert entering_permissions == read_write_permissions


@pytest.mark.asyncio
async def test_commandMove_noArgsProvided(move_context, engine):
    await move_logic(move_context, [], engine)
    assert len(move_context.channel.messages) == 1
    expected_message = 'Please specify a location to move to! For example: !move hawaii'
    assert move_context.channel.messages[0] == expected_message
    assert len(move_context.guild.channels[1].messages) == 0


@pytest.mark.asyncio
async def test_commandMove_nonexistantZone(move_context, engine):
    await move_logic(move_context, ['nowhere'], engine)
    assert len(move_context.channel.messages) == 1
    expected_message = 'You cannot travel to nowhere from town-square'
    assert move_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandMove_notInZoneChannel(move_context, non_zone_channel, engine):
    move_context.channel = non_zone_channel
    await move_logic(move_context, ['marketplace'], engine)
    assert len(move_context.channel.messages) == 0
    assert len(move_context.guild.channels[1].messages) == 0


@pytest.mark.asyncio
async def test_commandMove_nonadjacentZone(move_context, engine):
    await move_logic(move_context, ['throne-room'], engine)
    assert len(move_context.channel.messages) == 1
    expected_message = 'You cannot travel to throne-room from town-square'
    assert move_context.channel.messages[0] == expected_message
