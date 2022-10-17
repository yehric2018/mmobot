import discord
from discord import Permissions

import pytest
import pytest_asyncio
from sqlalchemy.orm import Session

from mmobot.commands import move_logic
from mmobot.db.models.player import Player
from mmobot.test.db import (
    add_player,
    delete_all_entities,
    get_player_with_name,
    init_test_engine,
)
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel, MockThread

DEFAULT_PERMISSIONS = 0


engine = init_test_engine()


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture
def moving_member():
    return MockMember(100, 'member')


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    add_player(session, Player(
        id=1,
        name='player',
        discord_id=100,
        is_active=True,
        zone='town-square'
    ))
    yield
    delete_all_entities(session)


@pytest.fixture
def no_permissions():
    return Permissions(DEFAULT_PERMISSIONS)


@pytest.fixture
def read_write_permissions():
    return Permissions(DEFAULT_PERMISSIONS, read_messages=True, send_messages=True)


@pytest.fixture
def read_only_permissions():
    return Permissions(DEFAULT_PERMISSIONS, read_messages=True, send_messages=False)


@pytest_asyncio.fixture
async def moving_thread():
    return MockThread(71, 'bell-tower', category='World')


@pytest_asyncio.fixture
async def current_channel(moving_member, moving_thread):
    channel = MockTextChannel(11, 'town-square', category='World')
    await channel.set_permissions(
        moving_member,
        read_messages=True,
        send_messages=False
    )
    channel.add_thread(moving_thread)
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
async def test_commandMove_zoneToZone(
        move_context, moving_member, session, no_permissions, read_write_permissions):
    await move_logic(move_context, ['marketplace'], engine)

    assert len(move_context.channel.messages) == 1
    leaving_message = '<@100> has left for <#12>.'
    assert move_context.channel.messages[0] == leaving_message

    assert len(move_context.guild.channels[1].messages) == 1
    entering_message = '<@100> has arrived.'
    assert move_context.guild.channels[1].messages[0] == entering_message

    leaving_permissions = move_context.channel.permissions_for(moving_member)
    assert leaving_permissions == no_permissions
    entering_permissions = move_context.guild.channels[1].permissions_for(moving_member)
    assert entering_permissions == read_write_permissions

    player = get_player_with_name(session, 'player')
    assert player.zone == 'marketplace'


@pytest.mark.asyncio
async def test_commandMove_zoneToMinizone(
    move_context, moving_member, session, read_only_permissions, read_write_permissions
):
    await move_logic(move_context, ['bell-tower'], engine)

    assert len(move_context.channel.messages) == 1
    leaving_message = '<@100> has entered <#71>.'
    assert move_context.channel.messages[0] == leaving_message

    dest_thread = move_context.channel.threads[0]
    assert len(dest_thread.messages) == 1
    entering_message = '<@100> has arrived.'
    assert dest_thread.messages[0] == entering_message

    leaving_permissions = move_context.channel.permissions_for(moving_member)
    assert leaving_permissions == read_only_permissions
    entering_permissions = dest_thread.permissions_for(moving_member)
    assert entering_permissions == read_write_permissions

    player = get_player_with_name(session, 'player')
    assert player.zone == 'bell-tower'


@pytest.mark.asyncio
async def test_commandMove_minizoneToZone(
    move_context, moving_thread, moving_member, session,
    read_only_permissions, read_write_permissions
):
    move_context.channel = moving_thread
    await move_logic(move_context, ['town-square'], engine)

    assert len(move_context.channel.messages) == 1
    leaving_message = '<@100> has left.'
    assert move_context.channel.messages[0] == leaving_message

    dest_channel = discord.utils.get(move_context.guild.channels, name='town-square')
    assert len(dest_channel.messages) == 0

    leaving_permissions = move_context.channel.permissions_for(moving_member)
    assert leaving_permissions == read_only_permissions
    entering_permissions = dest_channel.permissions_for(moving_member)
    assert entering_permissions == read_write_permissions

    player = get_player_with_name(session, 'player')
    assert player.zone == 'town-square'


@pytest.mark.asyncio
async def test_commandMove_noArgsProvided(move_context):
    await move_logic(move_context, [], engine)
    assert len(move_context.channel.messages) == 1
    expected_message = 'Please specify a location to move to! For example: !move hawaii'
    assert move_context.channel.messages[0] == expected_message
    assert len(move_context.guild.channels[1].messages) == 0


@pytest.mark.asyncio
async def test_commandMove_nonexistantZone(move_context, session):
    await move_logic(move_context, ['nowhere'], engine)
    assert len(move_context.channel.messages) == 1
    expected_message = 'You cannot travel to nowhere from town-square'
    assert move_context.channel.messages[0] == expected_message

    player = get_player_with_name(session, 'player')
    assert player.zone == 'town-square'


@pytest.mark.asyncio
async def test_commandMove_notInZoneChannel(move_context, non_zone_channel):
    move_context.channel = non_zone_channel
    await move_logic(move_context, ['marketplace'], engine)
    assert len(move_context.channel.messages) == 0
    assert len(move_context.guild.channels[1].messages) == 0


@pytest.mark.asyncio
async def test_commandMove_nonadjacentZone(move_context, session):
    await move_logic(move_context, ['throne-room'], engine)
    assert len(move_context.channel.messages) == 1
    expected_message = 'You cannot travel to throne-room from town-square'
    assert move_context.channel.messages[0] == expected_message

    player = get_player_with_name(session, 'player')
    assert player.zone == 'town-square'
