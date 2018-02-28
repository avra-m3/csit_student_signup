import time
import cv2

from information_getter import Transcriber

def capture():
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
    while 1:
        status, image = cam.read()
        # image = cv2.flip(image, 1)
        cv2.imshow('Camera', image)
        # print("loop")
        key = cv2.waitKey(1)
        if key == 32:
            im_name = 'image_cache/temp_' + str(time.time()) + '.png'
            cv2.imwrite(im_name, image)
            Transcriber.singleton.do(im_name)
        if key == 27:
            cv2.destroyAllWindows()
            return
 ,

def detect(image):
    # convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


Transcriber('output.csv')
capture()
