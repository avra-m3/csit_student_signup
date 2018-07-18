import os

import pytesseract
from PIL import Image
import cv2



def do(image):
    pytesseract.pytesseract.tesseract_cmd = os.getenv("tesseract_path")
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, image)

    # Get bounding box estimates
    print(pytesseract.image_to_boxes(Image.open(filename)))

    # Get verbose data including boxes, confidences, line and page numbers
    print(pytesseract.image_to_data(Image.open(filename)))
