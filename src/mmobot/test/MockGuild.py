from mmobot.test import MockTextChannel


class MockGuild:
    def __init__(self):
        self.channels = []

    def add_channel(self, channel: MockTextChannel):
        self.channels.append(channel)
