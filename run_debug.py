import time

import os

import cv2

from Card import Card
from config import Config

import traceback as tb
import numpy as np

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
    output_csv = open(Config.output_file, 'a')
else:
    raise IOError()

im_name = 'image_cache/temp_1519867122.4251614.png'

try:
    cv2.namedWindow(Config.window_name, cv2.WINDOW_NORMAL)
    img = cv2.imread(im_name, cv2.IMREAD_COLOR)
    cv2.imshow(Config.window_name, img)
    card = Card(path_to_json=im_name + ".response.json")
    print(card.get_student_id())
    print(card.get_names())
    sid_bounds = card.get_student_id().get_bounds()
    cv2.polylines(img, np.int32([np.array(sid_bounds.get_as_points())]), 1, (255, 255, 255))
    for field in card.get_names():
        bounds = field.get_bounds()
        cv2.polylines(img, np.int32([np.array(bounds.get_as_points())]), 1, (255, 255, 255))

    cv2.imshow(Config.window_name, img)
    key = cv2.waitKey(0)
    if key == Config.capture_key:
        insert_record(card.get_student_id().get_value(), card.name_as_str())
        cv2.destroyAllWindows()

except Exception as ex:
    print(ex.args)
    tb.print_exc()
