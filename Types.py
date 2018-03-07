import json
from typing import List

import regex
import sys

from config import Config

# class Coord:
#     def __init__(self, x = None, y = None):
#         self._x = x
#         self._y = y
#
#     def is_valid(self):
#         return self.x() is None
#
#     def x(self):



class BoundingBox:
    def __init__(self, data: json):
        self._raw = data
        self.is_valid = True

        for vector in data:
            if 'x' not in vector:
                self.invalidate()
            if 'y' not in vector:
                self.invalidate()
        if len(data) != 4:
            self.invalidate()
        else:
            self.topLeft, self.topRight, self.bottomRight, self.bottomLeft = data

    def invalidate(self):
        print("invalidated bounds: " + repr(self._raw))
        self.is_valid = False

    def get_as_points(self):
        if not self.is_valid:
            return []
        return [[self.tl('x'), self.tl('y')],
                [self.tr('x'), self.tr('y')],
                [self.br('x'), self.br('y')],
                [self.bl('x'), self.bl('y')]
                ]

    def _get_coord(self, coord, value=None)-> int or List[int]:
        if not self.is_valid:
            return -sys.maxsize - 1
        if value is None:
            return coord
        return coord[value]

    def tl(self, value=None) -> int or List[int]:
        self._get_coord(self.topLeft, value)

    def tr(self, value=None) -> int or List[int]:
        self._get_coord(self.topRight, value)

    def bl(self, value=None) -> int or List[int]:
        self._get_coord(self.bottomLeft, value)

    def br(self, value=None) -> int or List[int]:
        self._get_coord(self.bottomRight, value)

    def __str__(self):
        return "Box(%s,%s,%s,%s)" % (str(self.tl()), str(self.tr()), str(self.bl()), str(self.br()))


class TextField:
    matcher = None

    def __init__(self, data: json, type: str):
        self._raw = data
        self._bounds = None
        self.type = type
        self.set_bounds(data)

    def get_value(self) -> str:
        return self._raw["description"]

    def set_bounds(self, raw: dict):
        print(raw)
        self._bounds = BoundingBox(raw["boundingPoly"]["vertices"])

    def get_bounds(self) -> BoundingBox:
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

    def validate_boundries(self, field):
        return self.get_bounds().is_valid or field.get_bounds().is_valid

    def is_above(self, field):
        if not self.validate_boundries(field):
            return False
        bounds = self.get_bounds()
        return bounds.bl('x') - Config.word_distance_horizontal <= field.get_bounds().tl('x') <= bounds.bl(
            'x') + Config.word_distance_horizontal and bounds.bl('y') < field.get_bounds().tl('y')
        # and \
        # bounds.bl('y') <= field.get_bounds().tl('y') <= bounds.bl('y') + Config.word_distance_vertical_max

    def is_below(self, field):
        if not self.validate_boundries(field):
            return False
        bounds = self.get_bounds()
        return bounds.bl('x') - Config.word_distance_horizontal <= field.get_bounds().tl('x') <= bounds.bl(
            'x') + Config.word_distance_horizontal and bounds.tl('y') - Config.word_distance_vertical_min > \
               field.get_bounds().bl('y')
        #    and \
        #    bounds.tl('y') - Config.word_distance_vertical_min >= field.get_bounds().bl('y') >= bounds.tl(
        # 'y') - Config.word_distance_vertical_max

    def is_left_of(self, field):
        if not self.validate_boundries(field):
            return False
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
    matcher = regex.compile('^((?!Expiry)[A-Z][a-z]+\-?)+$')

    def __init__(self, data: json):
        super().__init__(data, "First Name")


class LastNameField(TextField):
    matcher = regex.compile('^([A-Z\-]+)$')

    def __init__(self, data: json):
        super().__init__(data, "Last Name")
