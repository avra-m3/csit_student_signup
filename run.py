import os
import time

import cv2
import numpy as np

from Types import StudentIDField
from config import Config
from Card import Card

import traceback as tb


def insert_record(snumber: str, name: str) -> None:
    now = time.localtime()
    output_csv.write(
        "s%s,%s,s%s@student.rmit.edu.au,%s\n" % (snumber, name, snumber, "%.4d/%.2d/%.2d %.2d:%.2d" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)))
    output_csv.flush()


if not os.path.exists(Config.output_file):
    output_csv = open(Config.output_file, "w")
    output_csv.write("snumber,name,email,time\n")
elif os.path.isfile(Config.output_file):
    output_csv = open(Config.output_file, 'a+')
else:
    raise IOError()


def capture():
    cam = cv2.VideoCapture(Config.target_camera)
    if not os.path.isdir(Config.temp_image_dir):
        os.mkdir(Config.temp_image_dir)
    cv2.namedWindow(Config.window_name, cv2.WINDOW_NORMAL)
    while True:
        status, image = cam.read()
        if Config.should_flip:
            image = cv2.flip(image, 1)
        cv2.imshow(Config.window_name, image)
        key = cv2.waitKey(1)
        if key == Config.capture_key:
            im_name = Config.temp_image_dir + '/temp_' + str(time.time()) + '.png'
            cv2.imwrite(im_name, image)
            card = None
            try:
                card = Card(path_to_image=im_name)
                print(card.get_student_id())
                print(card.get_names())
                sid_bounds = card.get_student_id().get_bounds()
                cv2.polylines(image, np.int32([np.array(sid_bounds.get_as_points())]), 1, (255, 255, 255))
                for field in card.get_names():
                    bounds = field.get_bounds()
                    cv2.polylines(image, np.int32([np.array(bounds.get_as_points())]), 1, (255, 255, 255))

                cv2.imshow(Config.window_name, image)
                if cv2.waitKey(0) == Config.capture_key:
                    insert_record(card.get_student_id().get_value(), card.name_as_str())

            except Exception as ex:
                print(ex.args)
                if card is None:
                    pass
                    # TODO: make image greyscale
                else:
                    if type(card.student_number) is StudentIDField:
                        cv2.polylines(image, np.int32([np.array(card.student_number.get_as_points())]), 1, (0, 0, 255))
                    if len(card.names) > 0:
                        for field in card.names:
                            bounds = field.get_bounds()
                            cv2.polylines(image, np.int32([np.array(bounds.get_as_points())]), 1, (0, 0, 255))
                cv2.im_show(Config.window_name, image)
                tb.print_exc()

        if key == Config.exit_key:
            cv2.destroyAllWindows()
            return


capture()
output_csv.close()
