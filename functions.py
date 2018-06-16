import json
import os
import time
import traceback as tb

import cv2
import numpy as np

import Config
from Card import Card
from Exceptions import BadRequestResponse, UncertainMatchException, NoMatchException, BadBoundingException


def highlight_fields(image, fields, colour, show_text=False):
    for field in fields:
        bounds = field.get_bounds()
        try:
            cv2.polylines(image, np.int32([np.array(bounds.get_as_points())]), 1, colour)
            if show_text:
                cv2.putText(image, field.get_value() + "(" + field.get_field_type() + ")",
                            (bounds.br('x') + 5, bounds.br('y')),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, .5, Config.Colors.outline, 3)
                cv2.putText(image, field.get_value() + "(" + field.get_field_type() + ")",
                            (bounds.br('x') + 5, bounds.br('y')),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, .5, Config.Colors.neutral, 1)
        except ValueError:
            print("Value Error: " + field)
        except TypeError:
            print(bounds)
    return image



def get_camera():
    cam = cv2.VideoCapture(Config.target_camera)
    return cam


def cv2_init():
    cv2.namedWindow(Config.window_name, cv2.WINDOW_NORMAL)


def wait_for_user() -> int:
    return cv2.waitKey(0)


def capture(cam):
    status, image = cam.read()
    if Config.should_flip:
        image = cv2.flip(image, 1)
    return image


def autosave_image(image):
    if os.getenv("RUN_MODE") == "DEBUG":
        return
    im_name = Config.temp_image_dir + '/temp_' + str(time.time()) + '.png'
    cv2.imwrite(im_name, image)
    return im_name


def process_image(path_to_image) -> Card:
    try:
        card = Card(path_to_image=path_to_image)
    except BadRequestResponse as ex:
        card = None
        tb.print_exc()
    return card


def process_JSON(path_to_json: json) -> Card:
    try:
        card = Card(path_to_json=path_to_json)
    except BadRequestResponse as ex:
        card = None
        tb.print_exc()
    return card


def output_card_to_image(card: Card, image):
    try:
        try:
            card.get_student_id()
            card.get_names()
            highlight_fields(image, card.get_field_results(), Config.Colors.neutral)
            highlight_fields(image, card.get_valid_fields(), Config.Colors.success, True)
            cv2.imshow(Config.window_name, image)
        except (UncertainMatchException, NoMatchException):
            highlight_fields(image, card.get_field_results(), Config.Colors.failure)
            highlight_fields(image, card.get_valid_fields(), Config.Colors.success, True)
    except BadBoundingException:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        highlight_fields(image, card.get_valid_fields(), Config.Colors.failure, True)
    return image
