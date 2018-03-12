import json
from typing import List

import regex
import Config

from Exceptions import BadBoundingException


class BoundingBox:
    def __init__(self, data: json):
        if len(data) != 4:
            raise BadBoundingException(data)
        self.topLeft, self.topRight, self.bottomRight, self.bottomLeft = data
        self.points = []
        for vector in data:
            if len(vector) != 2:
                raise BadBoundingException
            self.points.append(list(vector.values()))

    def get_as_points(self):
        return self.points

    @staticmethod
    def _safely_get_param(param: dict, value: str = None) -> int or List[int]:
        if value != 'x' and value != 'y':
            return param
        if type(param) is not dict or len(param) != 2:
            raise TypeError(param)
        if value not in param:
            return param[0]
        return param[value]

    def tl(self, value=None):
        return self._safely_get_param(self.topLeft, value)

    def tr(self, value=None):
        return self._safely_get_param(self.topRight, value)

    def bl(self, value=None):
        return self._safely_get_param(self.bottomLeft, value)

    def br(self, value=None):
        return self._safely_get_param(self.bottomRight, value)

    def __str__(self):
        return "Box%s" % (str(self.get_as_points()))


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
        match = self.matcher.match(self.get_value())
        if match is None:
            return False
        return match

    def is_above(self, field):
        bounds = self.get_bounds()
        min_x = bounds.bl('x') - Config.word_distance_horizontal
        max_x = bounds.bl('x') + Config.word_distance_horizontal
        return min_x <= field.get_bounds().tl('x') <= max_x and bounds.bl('y') < field.get_bounds().tl('y')

    def is_below(self, field):
        bounds = self.get_bounds()
        min_x = bounds.bl('x') - Config.word_distance_horizontal
        max_x = bounds.bl('x') + Config.word_distance_horizontal
        return min_x <= field.get_bounds().tl('x') <= max_x and bounds.tl('y') - field.get_bounds().bl('y')

    def is_left_of(self, field):
        bounds = self.get_bounds()
        min_y_1 = bounds.tr('y') - Config.word_distance_horizontal / 2
        max_y_1 = bounds.tr('y') + Config.word_distance_horizontal / 2
        min_y_2 = bounds.br('y') - Config.word_distance_horizontal / 2
        max_y_2 = bounds.br('y') + Config.word_distance_horizontal / 2

        return bounds.tr('x') < field.get_bounds().tl('x') < bounds.tr('x') + Config.word_distance_horizontal and \
             min_y_1 < field.get_bounds().tl('y') < max_y_1 and min_y_2 < field.get_bounds().bl('y') < max_y_2

    def __str__(self):
        return self.get_value()

    def __repr__(self):
        return "%s(%s) at %s" % (self.get_field_type(), self.get_value(), self.get_bounds())


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
