import os

import cv2
import imutils
import numpy as np
import pytesseract
from imutils import contours

pytesseract.pytesseract.tesseract_cmd = os.getenv("tesseract_path")

image = "../cache/20180616235138.temp.png"

def do(image, name):
    # load the example image and convert it to grayscale
    image = cv2.imread(image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # compute the Scharr gradient magnitude representation of the images
    # in both the x and y direction using OpenCV 2.4
    ddepth = cv2.cv.CV_32F if imutils.is_cv2() else cv2.CV_32F
    gradX = cv2.Sobel(gray, ddepth=ddepth, dx=1, dy=0, ksize=-3)
    gradY = cv2.Sobel(gray, ddepth=ddepth, dx=0, dy=1, ksize=3)

    # subtract the y-gradient from the x-gradient
    gradient = cv2.subtract(gradX, gradY)

    gradX = cv2.Sobel(gradient, ddepth=ddepth, dx=1, dy=0, ksize=-1)
    # gradY = cv2.Sobel(gradient, ddepth=ddepth, dx=0, dy=1, ksize=-1)

    gradient = cv2.subtract(gradX, gradY)


    gradient = cv2.convertScaleAbs(gradient)
    gradient = cv2.erode(gradient, None, iterations=2)

    blurred = cv2.blur(gradient, (9, 9))
    (_, thresh) = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # perform a series of erosions and dilations
    closed = cv2.erode(closed, None, iterations=20)
    closed = cv2.dilate(closed, None, iterations=20)

    closed = closed

    refCnts = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_NONE)
    refCnts = refCnts[0] if imutils.is_cv2() else refCnts[1]
    refCnts = contours.sort_contours(refCnts, method="left-to-right")[0]
    cv2.drawContours(image, refCnts, -1, (0, 255, 0), 3)    # for (i, c) in enumerate(refCnts):
    #     (x, y, w, h) = cv2.boundingRect(c)
    #     l = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
    #     # print(l)
    #     cv2.polylines(image, np.int32([np.array(l)]), 1, (0, 255, 0))
    # cv2.imshow(name, image)
    return image
for path in os.listdir('../cache/'):
    if path.endswith('.temp.png'):
        do("../cache/" + path,path)
# filename = "{}.png".format(os.getpid())
cv2.waitKey(0)
# cv2.imwrite(filename, gray)

# Get bounding box estimates
# print(pytesseract.image_to_boxes(Image.open(filename)))
