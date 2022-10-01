from discord import Member, PermissionOverwrite, Permissions, Role, TextChannel, User


ZONE_PERMISSIONS_NOT_IN = 384399657025


class MockTextChannel(TextChannel):
    def __init__(self, name):
        self.name = name
        self.permissions = {}
        self.messages = []

    def permissions_for(self, obj, /) -> Permissions:
        if isinstance(obj, Member) and obj in self.permissions:
            allow, _ = self.permissions[obj].from_pair()
            read_messages = allow.read_messages
            send_messages = allow.send_messages
        permissions = Permissions(ZONE_PERMISSIONS_NOT_IN, read_messages, send_messages)
        return permissions

    async def send(self, message):
        self.messages.append(message)

    async def set_permissions(self, target, **permissions):
        if not (isinstance(target, User) or isinstance(target, Role)):
            raise ValueError('target parameter must be either Member or Role')

        if len(permissions) == 0:
            raise ValueError('No overwrite provided.')
        try:
            overwrite = PermissionOverwrite(**permissions)
        except (ValueError, TypeError):
            raise TypeError('Invalid permissions given to keyword arguments.')

        self.permissions[target] = overwrite
