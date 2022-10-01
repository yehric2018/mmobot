from discord import Permissions

from mmobot.test.MockMember import MockMember


DEFAULT_PERMISSIONS = 0


class MockTextChannel:
    def __init__(self, name, permissions=Permissions(DEFAULT_PERMISSIONS)):
        self.name = name
        self.default_permissions = permissions
        self.permissions = {}
        self.messages = []

    def permissions_for(self, obj, /) -> Permissions:
        permissions = self.default_permissions
        if obj in self.permissions:
            member_permissions = self.permissions[obj]
            permissions.update(
                read_messages=member_permissions.read_messages,
                send_messages=member_permissions.send_messages
            )
        return permissions

    async def send(self, message):
        self.messages.append(message)

    async def set_permissions(self, target, read_messages, send_messages):
        if not isinstance(target, MockMember):
            raise ValueError('target parameter must be MockMember')

        overwrite = Permissions(
            DEFAULT_PERMISSIONS,
            read_messages=read_messages,
            send_messages=send_messages
        )

        self.permissions[target] = overwrite
