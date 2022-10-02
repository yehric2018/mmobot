class MockMember:
    def __init__(self, id, nick):
        self.id = id
        self.nick = nick
        self.mention = f'<@{self.id}>'

    async def edit(self, nick=None):
        if nick is not None:
            self.nick = nick

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id
