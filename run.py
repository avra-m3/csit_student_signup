import cv2

import Config
from utils import open_or_create_files, get_camera, wait_for_user, capture, process_image, insert_record, \
    autosave_image, output_card_to_image, cv2_init

camera = get_camera()
user_in = -1
output = open_or_create_files()
cv2_init()

while user_in != Config.exit_key:

    img = capture(camera)
    cv2.imshow(Config.window_name, img)

    user_in = cv2.waitKey(1)

    if user_in == Config.capture_key:
        img_path = autosave_image(img)
        card = process_image(img_path)
        img = output_card_to_image(card, img)
        cv2.imshow(Config.window_name, img)
        user_in = wait_for_user()
        if user_in == Config.capture_key:
            insert_record(output, card)
cv2.detroyAllWindows()


