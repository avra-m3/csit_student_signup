import cv2
import numpy as np

import Config
from Card import Card
from Exceptions import UncertainMatchException, NoMatchException, BadBoundingException


def highlight_fields(image, fields, colour, show_text=False):
    for field in fields:
        bounds = field.get_bounds()
        try:
            cv2.polylines(image, np.int32([np.array(bounds.get_as_points())]), 1, colour)
            if show_text:
                cv2.putText(image, field.get_value() + "(" + field.get_field_type() + ")",
                            (bounds.br('x') + 5, bounds.br('y')),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, .5, Config.Colors.outline, 2)
                cv2.putText(image, field.get_value() + "(" + field.get_field_type() + ")",
                            (bounds.br('x') + 5, bounds.br('y')),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, .5, Config.Colors.neutral, 1)
        except ValueError:
            print("Value Error: " + field)
        except TypeError:
            print(bounds)
    return image


def capture_2(cam):
    status, image = cam.read()
    if Config.should_flip:
        image = cv2.flip(image, 1)
    return status, image


def capture(cam):
    status, image = cam.read()
    if Config.should_flip:
        image = cv2.flip(image, 1)
    return image


def output_card_to_image(card: Card, image):
    try:
        card.get_student_id()
        card.get_names()
        if card.is_valid():
            highlight_fields(image, card.get_field_results(), Config.Colors.neutral)
            highlight_fields(image, card.get_valid_fields(), Config.Colors.success, True)
        else:
            highlight_fields(image, card.get_field_results(), Config.Colors.failure, True)
            highlight_fields(image, card.get_valid_fields(), Config.Colors.success, True)
    except BadBoundingException:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        highlight_fields(image, card.get_valid_fields(), Config.Colors.failure, True)
    return image
