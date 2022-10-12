from discord import Embed, Permissions
import pytest

from mmobot.test.mock import MockMember, MockTextChannel


DEFAULT_PERMISSIONS = 0


@pytest.fixture
def member():
    return MockMember(1, 'member1')


@pytest.fixture
def channel():
    return MockTextChannel(2, 'channel_name')


@pytest.fixture
def read_write_permissions():
    return Permissions(
        DEFAULT_PERMISSIONS,
        read_messages=True,
        send_messages=True
    )


def test_MockTextChannel_initialize(channel):
    assert channel is not None
    assert channel.name is not None
    assert channel.name == 'channel_name'
    assert channel.messages is not None
    assert len(channel.messages) == 0


def test_MockTextChannel_permissionsFor_default_read_write(member, channel):
    permissions = channel.permissions_for(member)
    assert permissions is not None
    assert permissions.read_messages is False
    assert permissions.send_messages is False


def test_MockTextChannel_permissionsFor_default_no_permissions(member, read_write_permissions):
    read_write_channel = MockTextChannel(1, 'channel_name', permissions=read_write_permissions)
    permissions = read_write_channel.permissions_for(member)
    assert permissions is not None
    assert permissions.read_messages is True
    assert permissions.send_messages is True


@pytest.mark.asyncio
async def test_MockTextChannel_setPermissions_to_read_write(member, channel):
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    permissions = channel.permissions_for(member)
    assert permissions.read_messages is True
    assert permissions.send_messages is True
    assert member in channel.members


@pytest.mark.asyncio
async def test_MockTextChannel_setPermissions_to_no_permissions(member, channel):
    await channel.set_permissions(member, read_messages=False, send_messages=False)
    permissions = channel.permissions_for(member)
    assert permissions.read_messages is False
    assert permissions.send_messages is False
    assert member not in channel.members


@pytest.mark.asyncio
async def test_MockTextChannel_send(channel):
    await channel.send('TEST MESSAGE')
    assert len(channel.messages) == 1
    assert channel.messages[0] == 'TEST MESSAGE'


@pytest.mark.asyncio
async def test_MockChannel_sendWithEmbed(channel):
    embed = Embed(
        title='Embed title',
        description='description'
    )
    embed.add_field(name='field1', value='value1')
    await channel.send('', embed=embed)
    assert len(channel.messages) == 1
    expected_message = '<title>Embed title</title>\n<desc>description</desc>\n'
    expected_message += '<field>field1:value1</field>\n'
    assert channel.messages[0] == expected_message
