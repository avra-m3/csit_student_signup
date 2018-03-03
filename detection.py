import time
import cv2
import os

from config import Config
from information_getter import Transcriber


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
                result = Transcriber.singleton.do(im_name)
                with open(im_name + ".results.csv", "w+") as temp_f:
                    temp_f.write(result)
            except Exception as ex:
                print("Failed, two first names?")

        if key == Config.exit_key:
            cv2.destroyAllWindows()
            return


Transcriber(Config.output_file)
capture()
