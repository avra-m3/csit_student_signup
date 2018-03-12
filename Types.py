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
            self.points.append(list(vector.values()))

    def get_as_points(self):
        return self.points

    @staticmethod
    def _safely_get_param(param: dict, value: str = None) -> int or List[int]:
        if value != "x" or value != "y":
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
        return bounds.bl('x') - Config.word_distance_horizontal <= field.get_bounds().tl('x') <= bounds.bl(
            'x') + Config.word_distance_horizontal and bounds.bl('y') < field.get_bounds().tl('y')
        # and \
        # bounds.bl('y') <= field.get_bounds().tl('y') <= bounds.bl('y') + Config.word_distance_vertical_max

    def is_below(self, field):
        bounds = self.get_bounds()
        return bounds.bl('x') - Config.word_distance_horizontal <= field.get_bounds().tl('x') <= bounds.bl(
            'x') + Config.word_distance_horizontal and bounds.tl('y') - Config.word_distance_vertical_min > \
               field.get_bounds().bl('y')
        #    and \
        #    bounds.tl('y') - Config.word_distance_vertical_min >= field.get_bounds().bl('y') >= bounds.tl(
        # 'y') - Config.word_distance_vertical_max

    def is_left_of(self, field):
        bounds = self.get_bounds()
        return bounds.tr('x') < field.get_bounds().tl('x') < bounds.tr('x') + Config.word_distance_horizontal and \
               bounds.tr('y') - Config.word_distance_horizontal / 2 < field.get_bounds().tl('y') < bounds.tr(
            'y') + Config.word_distance_horizontal / 2 \
               and bounds.br('y') - Config.word_distance_horizontal / 2 < field.get_bounds().bl('y') < bounds.br(
            'y') + Config.word_distance_horizontal / 2

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
