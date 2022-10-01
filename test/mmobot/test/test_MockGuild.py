import discord

from mmobot.test import MockGuild, MockTextChannel


def test_MockGuild_initialize():
    guild = MockGuild()
    assert guild is not None
    assert guild.channels is not None
    assert guild.channels == []


def test_MockGuild_add_channel():
    guild = MockGuild()
    channel = MockTextChannel('channel1')
    guild.add_channel(channel)
    found_channel = discord.utils.get(guild.channels, name='channel1')
    assert found_channel.name is not None
    assert found_channel.name == 'channel1'
