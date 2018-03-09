import time

import os
import Config
import cv2

from Card import Card

import traceback as tb
import numpy as np

from Types import TextField


# def insert_record(snumber: str, name: str) -> None:
#     now = time.localtime()
#     output_csv.write(
#         "s%s,%s,s%s@student.rmit.edu.au,%s\n" % (snumber, name, snumber, "%.4d/%.2d/%.2d %.2d:%.2d" % (
#             now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)))
#     output_csv.flush()


def json_to_field(image, list, colour, show_text=False):
    field_list = []
    for field in list:
        field_list.append(TextField(field, "Generic"))
    # display_fields(image, field_list, colour, show_text)
    return field_list


def display_fields(image, fields, colour, show_text=False):
    bounds =  None
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


def test(file_name):
    # if not os.path.exists(Config.output_file):
    #     output_csv = open(Config.output_file, "w")
    #     output_csv.write("snumber,name,email,time\n")
    # elif os.path.isfile(Config.output_file):
    #     output_csv = open(Config.output_file, 'a')
    # else:
    #     raise IOError()

    im_name = "image_cache/" + file_name + ".png"
    json_name = "image_cache/" + file_name + ".png.response.json"
    cv2.namedWindow(Config.window_name, cv2.WINDOW_NORMAL)
    image = cv2.imread(im_name, cv2.IMREAD_COLOR)
    cv2.imshow(Config.window_name, image)

    valid_fields = []
    all_values = []
    try:
        card = Card(path_to_json=json_name)

        all_values = card.get_text_results()

        valid_fields.append(card.get_student_id())
        valid_fields.extend(card.get_names())

        convert_and_display_json(image, all_values, Config.Colors.neutral, True)
        display_fields(image, valid_fields, Config.Colors.success, True)

        cv2.imshow(Config.window_name, image)

        if cv2.waitKey(0) == Config.capture_key:
            pass
        #     insert_record(card.get_student_id().get_value(), card.name_as_str())

        cv2.destroyAllWindows()

    except Exception:
        tb.print_exc()
        convert_and_display_json(image, all_values, Config.Colors.failure, True)
        display_fields(image, valid_fields, Config.Colors.success)

        cv2.imshow(Config.window_name, image)
        cv2.waitKey(0)


for item in os.listdir("errs"):
    if item.endswith(".response.json"):
        test(item.strip(".png.response.json"))
