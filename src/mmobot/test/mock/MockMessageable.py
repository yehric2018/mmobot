from discord import Permissions

from mmobot.constants import PERMISSIONS_DEFAULT
from mmobot.test.mock import MockCategory, MockMember


class MockMessageable():
    def __init__(self, id, name, permissions=None, category='General'):
        self.id = id
        self.mention = f'<#{self.id}>'
        self.name = name
        self.messages = []
        self.members = []
        if permissions is None:
            permissions = Permissions(PERMISSIONS_DEFAULT)
        self.default_permissions = permissions
        self.permissions = {}
        self.members = []
        self.category = MockCategory(category)

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
            for field in embed.fields:
                message += f'<field>{field.name}:{field.value}</field>\n'
        self.messages.append(message)

    async def set_permissions(self, member: MockMember, read_messages, send_messages):
        overwrite = Permissions(
            PERMISSIONS_DEFAULT,
            read_messages=read_messages,
            send_messages=send_messages
        )
        self.permissions[member] = overwrite

        if member not in self.members and (read_messages or send_messages):
            self.members.append(member)
        elif member in self.members and not read_messages and not send_messages:
            self.members.remove(member)
