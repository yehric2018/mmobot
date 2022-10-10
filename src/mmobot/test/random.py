class MockRandomInt:
    def __init__(self, values):
        self.values = iter(values)
        self.calls = []

    def next(self, min, max):
        self.calls.append((min, max))
        return next(self.values)
