import pytest
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel


TEST_MESSAGE = 'test message'


@pytest.fixture
def sending_member():
    return MockMember(1, 'member1')


@pytest.fixture
def sending_channel():
    return MockTextChannel(1, 'channel1')


@pytest.fixture
def non_sending_channel():
    return MockTextChannel(2, 'channel2')


@pytest.fixture
def sending_guild(sending_channel, non_sending_channel):
    guild = MockGuild()
    guild.add_channel(sending_channel)
    guild.add_channel(non_sending_channel)
    return guild


def test_MockContext_initialize(sending_member, sending_channel, sending_guild):
    context = MockContext(sending_member, sending_channel, sending_guild)
    assert context is not None
    assert context.author is not None
    assert context.author.id == 1
    assert context.author.nick == 'member1'
    assert context.channel is not None
    assert context.channel.name == 'channel1'
    assert context.guild is not None
    assert context.guild.channels is not None
    assert len(context.guild.channels) == 2
    assert context.guild.channels[0].name == 'channel1'
    assert context.guild.channels[1].name == 'channel2'


@pytest.mark.asyncio
async def test_MockContext_send(sending_member, sending_channel, sending_guild):
    context = MockContext(sending_member, sending_channel, sending_guild)
    await context.send(TEST_MESSAGE)
    assert len(context.channel.messages) == 1
    assert context.channel.messages[0] == TEST_MESSAGE
    assert len(sending_channel.messages) == 1
    assert sending_channel.messages[0] == TEST_MESSAGE
    assert len(sending_guild.channels[0].messages) == 1
    assert sending_guild.channels[0].messages[0] == TEST_MESSAGE
    assert len(sending_guild.channels[1].messages) == 0
