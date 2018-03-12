import cv2
import os

import Config
from utils import open_or_create_files, get_camera, wait_for_user, capture, process_JSON, output_card_to_image, cv2_init


def pre_setup():
    cv2_init()


def process(file_name):
    im_name = "image_cache/" + file_name + ".png"
    json_name = "image_cache/" + file_name + ".png.response.json"
    img = cv2.imread(im_name)
    card = process_JSON(path_to_json=json_name)
    img = output_card_to_image(card, img)
    cv2.imshow(Config.window_name, img)
    wait_for_user()


pre_setup()
for file in os.listdir("image_cache"):
    if file.endswith(".png.response.json"):
        path = file.strip(".png.response.json")
        if os.path.exists("image_cache/" + path + ".png"):
            process(path)
