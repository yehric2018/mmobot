from discord import Permissions

from mmobot.test.mock import MockMember


DEFAULT_PERMISSIONS = 0


class MockTextChannel:
    def __init__(self, id, name, permissions=None):
        if permissions is None:
            permissions = Permissions(DEFAULT_PERMISSIONS)
        self.id = id
        self.mention = f'<#{self.id}>'
        self.name = name
        self.default_permissions = permissions
        self.permissions = {}
        self.messages = []
        self.members = []

    def permissions_for(self, obj, /) -> Permissions:
        permissions = self.default_permissions
        if obj in self.permissions:
            member_permissions = self.permissions[obj]
            permissions.update(
                read_messages=member_permissions.read_messages,
                send_messages=member_permissions.send_messages
            )
        return permissions

    async def send(self, message='', embed=None):
        if embed is not None:
            message = ''
            message += f'<title>{embed.title}</title>\n'
            message += f'<desc>{embed.description}</desc>\n'
            print(repr(embed.description))
        self.messages.append(message)

    async def set_permissions(self, member: MockMember, read_messages, send_messages):
        overwrite = Permissions(
            DEFAULT_PERMISSIONS,
            read_messages=read_messages,
            send_messages=send_messages
        )
        self.permissions[member] = overwrite

        if member not in self.members and (read_messages or send_messages):
            self.members.append(member)
        elif member in self.members and not read_messages and not send_messages:
            self.members.remove(member)
