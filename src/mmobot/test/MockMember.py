class MockMember:
    def __init__(self, id, nick):
        self.id = id
        self.nick = nick
        self.mention = f'<@{self.id}>'

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id
