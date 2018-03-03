import json

from Exceptions import InvalidResponseException


class TextField:
    def __init__(self, data: json):
        if data is not None:
            set(data)

    def set(self, data: json) -> None:
        self.value = data
        self.bounds = BoundingBox(data["boundingPoly"]["vertices"])


class BoundingBox:
    def __init__(self, data: json):
        if len(data) != 4:
            raise InvalidResponseException("Bounds: " + str(data))
        self.topLeft, self.topRight, self.bottomLeft, self.bottomRight = data

    def get_distance(self, other) -> tuple:
        x = other.topLeft['x'] - self.topLeft['x']
        y = other.topLeft['y'] - self.topLeft['y']
        return x, y

    def tl(self, value=None):
        if value == 'x':
            return self.topLeft['x']
        elif value == 'y':
            return self.topLeft['y']
        else:
            return self.topLeft

    def tr(self, value=None):
        if value == 'x':
            return self.topRight['x']
        elif value == 'y':
            return self.topRight['y']
        else:
            return self.topRight

    def bl(self, value=None):
        if value == 'x':
            return self.bottomLeft['x']
        elif value == 'y':
            return self.bottomLeft['y']
        else:
            return self.bottomLeft

    def br(self, value=None):
        if value == 'x':
            return self.bottomRight['x']
        elif value == 'y':
            return self.bottomRight['y']
        else:
            return self.bottomRight
