import json

import regex

from Exceptions import InvalidResponseException
from config import Config


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

    def __str__(self):
        return "(%d,%d),(%d,%d),(%d,%d),(%d,%d)".format(*self.tl(), *self.tr(), *self.bl() * self.br())


class TextField:
    matcher = None

    def __init__(self, data: json, type: str):
        self._raw = data
        self._bounds = None
        self.type = type

    def get_value(self) -> str:
        return self._raw["description"]

    def get_bounds(self) -> BoundingBox:
        if self._bounds is None:
            self._bounds = BoundingBox(self._raw["boundingPoly"]["vertices"])
        return self._bounds

    def get_field_type(self) -> str:
        return self.type

    def is_valid_field(self):
        if self.matcher is None:
            raise NotImplementedError()
        return self.matcher.match(self.get_value()) is None

    def is_above(self, field):
        bounds = self.get_bounds()
        return bounds.bl('x') - Config.word_gap <= field.get_bounds().tl('x') <= bounds.bl('x') + Config.word_gap and \
               bounds.bl('y') <= field.get_bounds.tl('y') <= bounds.bl('y') + Config.word_gap * 2

    def is_left_of(self, field):
        bounds = self.get_bounds()
        return bounds.tr('x') <= field.get_bounds().tl('x') <= bounds.tr('x') + Config.word_gap and \
               bounds.tr('y') - Config.word_gap / 2 <= field.get_bounds().tl('y') <= bounds.tr(
            'y') + Config.word_gap / 2 \
               and bounds.br('y') - Config.word_gap / 2 <= field.get_bounds().bl('y') <= bounds.br(
            'y') + Config.word_gap / 2

    def __str__(self):
        return "%s(%s) at %s".format(self.get_field_type(), self.get_value(), self.get_bounds())


class StudentIDField(TextField):
    matcher = regex.compile('^(\d{7})$')

    def __init__(self, data: json):
        super().__init__(data, "Student ID")


class FirstNameField(TextField):
    matcher = regex.compile('^((?!Expiry)[A-Z][a-z\-]+)$')

    def __init__(self, data: json):
        super().__init__(data, "First Name")


class LastNameField(TextField):
    matcher = regex.compile('^([A-Z\-]+)$')

    def __init__(self, data: json):
        super().__init__(data, "Last Name")
