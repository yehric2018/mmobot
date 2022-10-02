from mmobot.test.mock import MockGuild, MockMember, MockTextChannel


class MockContext:
    def __init__(self, author: MockMember, channel: MockTextChannel, guild: MockGuild):
        self.author = author
        self.channel = channel
        self.guild = guild

    async def send(self, message='', embed=None):
        await self.channel.send(message=message, embed=embed)
