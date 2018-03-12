import os
import time
import traceback as tb
from typing import Tuple

import cv2

import Config
import Helpers
from Card import Card
from Exceptions import *


def open_or_create_files():
    if not os.path.exists(Config.output_file):
        output_csv = open(Config.output_file, "w")
        output_csv.write("snumber,name,email,time\n")
    elif os.path.isfile(Config.output_file):
        output_csv = open(Config.output_file, 'a+')
    else:
        raise IOError()
    if not os.path.isdir(Config.temp_image_dir):
        os.mkdir(Config.temp_image_dir)
    return output_csv


def get_camera():
    cam = cv2.VideoCapture(Config.target_camera)
    cv2.namedWindow(Config.window_name, cv2.WINDOW_NORMAL)
    return cam


def get_user_response() -> int:
    return cv2.waitKey(0)


def capture(cam):
    status, image = cam.read()
    if Config.should_flip:
        image = cv2.flip(image, 1)
    return image


def process(image) -> Tuple[object, Card]:
    im_name = Config.temp_image_dir + '/temp_' + str(time.time()) + '.png'
    cv2.imwrite(im_name, image)
    try:
        card = Card(path_to_image=im_name)
        card.get_student_id()
        card.get_names()
    except BadRequestResponse as ex:
        card = None
        tb.print_exc()

    try:
        Helpers.display_fields(image, card.get_field_results(), Config.Colors.neutral)
        Helpers.display_fields(image, card.get_valid_fields(), Config.Colors.success, True)
        cv2.imshow(Config.window_name, image)
    except (UncertainMatchException, NoMatchException):
        Helpers.display_fields(image, card.get_field_results(), Config.Colors.failure)
        Helpers.display_fields(image, card.get_valid_fields(), Config.Colors.success, True)
    except BadBoundingException:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        Helpers.display_fields(image, card.get_valid_fields(), Config.Colors.failure, True)
    return card, image


camera = get_camera()
user_in = -1
output = open_or_create_files()
while user_in != Config.exit_key:
    img = capture(camera)
    cv2.imshow(Config.window_name, img)
    user_in = cv2.waitKey(1)
    if user_in == Config.capture_key:
        scard, img = process(img)
        cv2.imshow(Config.window_name, img)
        user_in = get_user_response()
        if user_in == Config.capture_key:
            Helpers.insert_record(output, scard)
cv2.detroyAllWindows()
