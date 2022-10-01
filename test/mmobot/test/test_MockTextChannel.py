import pytest
from mmobot.test import MockTextChannel


ZONE_PERMISSIONS_IN = 384399657025
ZONE_PERMISSIONS_NOT_IN = 384399657025


def test_mock_text_channel_initialize():
    channel = MockTextChannel('channel_name')
    assert channel is not None
    assert channel.name is not None
    assert channel.name == 'channel_name'
    assert channel.messages is not None
    assert len(channel.messages) == 0


def test_mock_text_channel_set_permissions_for():
    pass


@pytest.mark.asyncio
async def test_mock_text_channel_send():
    channel = MockTextChannel('channel_name')
    await channel.send('TEST MESSAGE')
    assert len(channel.messages) == 1
    assert channel.messages[0] == 'TEST MESSAGE'
