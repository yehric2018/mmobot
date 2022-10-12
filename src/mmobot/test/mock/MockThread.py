from discord import Permissions

from mmobot.constants import PERMISSIONS_DEFAULT
from mmobot.test.mock.MockMessageable import MockMessageable


class MockThread(MockMessageable):
    def __init__(self, id, name, category='General'):
        permissions = Permissions(
            PERMISSIONS_DEFAULT,
            read_messages=True,
            send_messages=False
        )
        super().__init__(id, name, permissions, category=category)

    async def add_user(self, user):
        await self.set_permissions(user, read_messages=True, send_messages=True)

    async def remove_user(self, user):
        await self.set_permissions(user, read_messages=True, send_messages=False)
