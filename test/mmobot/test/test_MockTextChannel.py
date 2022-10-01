from discord import Permissions
import pytest

from mmobot.test import MockTextChannel
from mmobot.test.MockMember import MockMember


DEFAULT_PERMISSIONS = 0


@pytest.fixture
def read_write_permissions():
    return Permissions(
        DEFAULT_PERMISSIONS,
        read_messages=True,
        send_messages=True
    )


def test_MockTextChannel_initialize():
    channel = MockTextChannel('channel_name')
    assert channel is not None
    assert channel.name is not None
    assert channel.name == 'channel_name'
    assert channel.messages is not None
    assert len(channel.messages) == 0


def test_MockTextChannel_permissionsFor_default_read_write():
    member = MockMember(1, 'member1')
    channel = MockTextChannel('channel_name')
    permissions = channel.permissions_for(member)
    assert permissions is not None
    assert permissions.read_messages is False
    assert permissions.send_messages is False


def test_MockTextChannel_permissionsFor_default_no_permissions(read_write_permissions):
    member = MockMember(1, 'member1')
    channel = MockTextChannel('channel_name', permissions=read_write_permissions)
    permissions = channel.permissions_for(member)
    assert permissions is not None
    assert permissions.read_messages is True
    assert permissions.send_messages is True


@pytest.mark.asyncio
async def test_MockTextChannel_setPermissions_to_read_write():
    member = MockMember(1, 'member1')
    channel = MockTextChannel('channel_name')
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    permissions = channel.permissions_for(member)
    assert permissions.read_messages is True
    assert permissions.send_messages is True


@pytest.mark.asyncio
async def test_MockTextChannel_setPermissions_to_no_permissions():
    member = MockMember(1, 'member1')
    channel = MockTextChannel('channel_name')
    await channel.set_permissions(member, read_messages=False, send_messages=False)
    permissions = channel.permissions_for(member)
    assert permissions.read_messages is False
    assert permissions.send_messages is False


@pytest.mark.asyncio
async def test_MockTextChannel_send():
    channel = MockTextChannel('channel_name')
    await channel.send('TEST MESSAGE')
    assert len(channel.messages) == 1
    assert channel.messages[0] == 'TEST MESSAGE'
