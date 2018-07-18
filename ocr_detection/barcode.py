import cv2
import imutils
import numpy as np
from pyzbar import pyzbar


def detect(image):
    # Convert to grayscale
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # compute the Scharr gradient magnitude representation of the images
    # in both the x and y direction using OpenCV 2.4
    ddepth = cv2.cv.CV_32F if imutils.is_cv2() else cv2.CV_32F

    gradX = cv2.Sobel(gray, ddepth=ddepth, dx=1, dy=0, ksize=-3)
    gradY = cv2.Sobel(gray, ddepth=ddepth, dx=0, dy=1, ksize=3)

    # subtract the y-gradient from the x-gradient
    gradient = cv2.subtract(gradX, gradY)

    # Repeat on the X gradient
    gradX = cv2.Sobel(gradient, ddepth=ddepth, dx=1, dy=0, ksize=-1)

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

    refCnts = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)
    refCnts = refCnts[0] if imutils.is_cv2() else refCnts[1]

    max_bounds = (0, 0, 0, 0)
    max_bounds_raw = ((0, 0), (0, 0), 0)
    max_index = -1

    for (i, c) in enumerate(refCnts):
        ((c_x, c_y), (w, h), angle) = cv2.minAreaRect(c)
        max_dim = max(w, h)
        min_dim = min(w, h)

        if w > max_bounds[2] and max_dim / 8 < min_dim < max_dim / 5 and min_dim > 50:
            max_bounds = (c_x, c_y, max_dim, min_dim, angle)
            max_index = i
            max_bounds_raw = ((c_x, c_y), (max_dim, min_dim), angle)

    cv2.drawContours(image, refCnts, max_index, (0, 255, 0), 3)
    box = cv2.boxPoints(max_bounds_raw)
    box = np.int0(box)
    cv2.drawContours(image, [box], 0, (0, 255, 0), 2)
    cv2.putText(image, '{},{}'.format(max_bounds[2], max_bounds[3]), (10, 50),
                cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 255, 0), 5)
    closed = cv2.cvtColor(closed, cv2.COLOR_GRAY2RGB)

    return closed, max_index, max_bounds


def optimise(image, barcode):
    x = int(barcode[0] - barcode[2] / 2)
    y = int((barcode[1] - barcode[3] / 2) - barcode[3] * 3)
    width = int(barcode[2] + 200)
    height = int(barcode[3] * 4)

    # print(x, y, width, height)
    crop = image[y:y + height, x:x + width]
    # if barcode[4] % 90 > 45:
    #     pass
    rotated = imutils.rotate(crop, barcode[4])
    scaled = cv2.resize(rotated, (width * 4, height * 4))
    gray = cv2.cvtColor(scaled, cv2.COLOR_BGR2GRAY)
    # sharpen1 = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    # thresh = cv2.equalizeHist(gray)
    # sharpened = cv2.filter2D(gray, -1, sharpen1)
    # (_, thresh) = cv2.threshold(thresh, 127, 255, cv2.THRESH_TRUN+cv2.THRESH_OTSU)

    # thresh = cv2.filter2D(thresh, -1, sharpen1)
    # thresh = cv2.filter2D(thresh, -1, sharpen1)
    # (_, thresh) = cv2.threshold(thresh, 127, 255, cv2.THRESH_TRUNC+cv2.THRESH_OTSU)
    # (_, thresh) = cv2.threshold(sharpened, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # for i in range(100, 200,5):
    # (_, a) = cv2.threshold(thresh, 100, 255, cv2.THRESH_BINARY)
    # cv2.imshow("", thresh)
    # thresh = cv2.dilate(thresh, None, iterations=1)

    return rotated


def detect_v2(frame):
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = imutils.resize(frame, width=400)
    barcodes = pyzbar.decode(frame)
    success = False
    for barcode in barcodes:
        polygon = barcode.polygon
        barcodeType = barcode.type
        barcodeData = barcode.data.decode("utf-8")

        if barcodeType != "CODE39" or len(barcodeData) != 14:
            continue

        success = True

        cv2.polylines(frame, np.array(polygon, np.int32), False, (0, 0, 255))
        text = "{} ({})".format(len(barcodeData), barcodeType)
        cv2.putText(frame, text, 0, cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)
    return frame, success, None
