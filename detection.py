import os
import time

import cv2

from config import Config
from information_getter import Card


def get_time_str() -> str:
    now = time.localtime()
    return "%.4d/%.2d/%.2d %.2d:%.2d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)


def insert_record(snumber: str, name: str) -> None:
    output_csv.write(
        "s%s,s%s@student.rmit.edu.au,%s,%s\n" % (snumber, name, snumber, self.get_time_str()))
    output_csv.flush()


if not os.path.exists(Config.output_file):
    output_csv = open(Config.output_file, "w")
    output_csv.write("snumber,name,email,time\n")
elif os.path.isfile(Config.output_file):
    output_csv = open(Config.output_file, 'a')
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
            try:
                card = Card(im_name)
                print(card.get_student_id())
                print(card.get_names())
                insert_record(card.get_student_id().get_value(), card.name_as_str())

            except Exception as ex:
                print(ex.args)

        if key == Config.exit_key:
            cv2.destroyAllWindows()
            return


capture()
output_csv.close()
