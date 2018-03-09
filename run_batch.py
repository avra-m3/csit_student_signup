import os
import time

from Card import Card
import Config


def insert_record(snumber: str, name: str) -> None:
    now = time.localtime()
    output_csv.write(
        "s%s,%s,s%s@student.rmit.edu.au,%s\n" % (snumber, name, snumber, "%.4d/%.2d/%.2d %.2d:%.2d" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)))
    output_csv.flush()


Config.output_file = "batch_" + Config.output_file
if not os.path.exists(Config.output_file):
    output_csv = open(Config.output_file, "w")
    output_csv.write("snumber,name,email,time\n")
elif os.path.isfile(Config.output_file):
    output_csv = open(Config.output_file, 'w')
else:
    raise IOError()

im_name = 'im_cache_temp\\csit_student_signup\\image_cache\\temp_1519863144.8123555.png'
for item in os.listdir('image_cache'):
    if item.endswith(".json"):
        try:
            # cv2.namedWindow(Config.window_name, cv2.WINDOW_NORMAL)
            # im_name = cv2.imread("image_cache/" + item.strip(".response.json"), cv2.IMREAD_COLOR)
            # cv2.imshow(Config.window_name, im_name)
            card = Card(path_to_json="image_cache/" + item)

            print(card.get_student_id())
            print(card.get_names())
            # sid_bounds = card.get_student_id().get_bounds()
            # cv2.polylines(im_name, np.int32([np.array(sid_bounds.get_as_points())]), 1, (255, 255, 255))
            # for field in card.get_names():
            #     bounds = field.get_bounds()
            #     cv2.polylines(im_name, np.int32([np.array(bounds.get_as_points())]), 1, (255, 255, 255))

            # cv2.imshow(Config.window_name, im_name)
            # key = cv2.waitKey(0)
            # if key == Config.capture_key:
            insert_record(card.get_student_id().get_value(), card.name_as_str())

        except Exception as ex:
            print("Failed: " + str(item) + " : " + str(type(ex)))
            with open("image_cache/" + item, "rb") as src:
                with open("errs/" + item, "wb") as out_f:
                    out_f.write(src.read())
            # print(ex.args)
            # tb.print_exc()
