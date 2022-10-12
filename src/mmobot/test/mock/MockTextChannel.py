from mmobot.test.mock import MockThread
from mmobot.test.mock.MockMessageable import MockMessageable


class MockTextChannel(MockMessageable):
    def __init__(self, id, name, permissions=None, category='General'):
        super().__init__(id, name, permissions=permissions, category=category)
        self.threads = []

    def add_thread(self, thread: MockThread):
        self.threads.append(thread)
