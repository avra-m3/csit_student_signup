class Cursor:
    def __init__(self, max, overflow=True):
        self.index = 0
        self.max = max
        self.overflow = overflow

    def increment(self):
        self.index += 1
        if self.index >= self.max:
            if self.overflow:
                self.index = 0
            else:
                self.index = self.max
