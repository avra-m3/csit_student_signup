import os
import time
import traceback as tb
from Exceptions import *
import cv2
import numpy as np

import Helpers
from Card import Card
import Config


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

def get_camera():
    cam = cv2.VideoCapture(Config.target_camera)
    cv2.namedWindow(Config.window_name, cv2.WINDOW_NORMAL)
    return cam

def capture():

    status, image = cam.read()
    if Config.should_flip:
        image = cv2.flip(image, 1)
    return image

    cv2.imshow(Config.window_name, image)
    key = cv2.waitKey(1)

        if key == Config.capture_key:

def process(image):
    im_name = Config.temp_image_dir + '/temp_' + str(time.time()) + '.png'
    cv2.imwrite(im_name, image)
    try:
        card = Card(path_to_image=im_name)
    except BadRequestResponse as ex:
        card = None
        tb.print_exc()

    try:
        Helpers.display_fields(image, card.get_field_results(), Config.Colors.neutral)
        Helpers.display_fields(image, card.get_valid_fields(), Config.Colors.success,True)
        cv2.imshow(Config.window_name, image)
    except (UncertainMatchException, NoMatchException):
        Helpers.display_fields(image, card.get_field_results(), Config.Colors.failure)
        Helpers.display_fields(image, card.get_valid_fields(), Config.Colors.success, True)
    except BadBoundingException:

                key = cv2.waitKey(0)
                if key == Config.capture_key:
                    insert_record(card.get_student_id().get_value(), card.name_as_str())

            except Exception as ex:
                print(ex.args)
                if card is None:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                else:
                    for field in all_fields:
                        bounds = field.get_bounds()
                        cv2.polylines(image, np.int32([np.array(bounds.get_as_points())]), 1, Config.Colors.failure)
                        cv2.putText(image, field.get_value() + "(" + field.get_field_type() + ")",
                                    (bounds.br('x') + 5, bounds.br('y')),
                                    cv2.FONT_HERSHEY_COMPLEX_SMALL, .5, Config.Colors.outline, 3)
                        cv2.putText(image, field.get_value() + "(" + field.get_field_type() + ")",
                                    (bounds.br('x') + 5, bounds.br('y')),
                                    cv2.FONT_HERSHEY_COMPLEX_SMALL, .5, Config.Colors.neutral, 1)
                cv2.imshow(Config.window_name, image)
                tb.print_exc()

        if key == Config.exit_key:
            cv2.destroyAllWindows()
            return


capture()
output_csv.close()
