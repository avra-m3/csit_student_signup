import json
import os
from base64 import b64encode

import cv2
import regex as regex
import requests
import time

import Config
from Types import TextField


class GCloudOCR:
    ENDPOINT = 'https://vision.googleapis.com/v1/images:annotate'
    AUTH = os.getenv('OCR_AUTH_KEY')
    HEADERS = {'Content-Type': 'application/json'}

    @staticmethod
    def format_image(image: bytes):
        return {
            'image': {'content': b64encode(image).decode()},
            "features": [
                {
                    "type": "TEXT_DETECTION"
                }
            ],
            "imageContext": {
                "languageHints": [
                    "en"
                ]
            }
        }

    @staticmethod
    def format_data(image: bytes):
        return json.dumps(
            {
                'requests': [GCloudOCR.format_image(image)]
            }
        )

    @staticmethod
    def push(image: bytes) -> requests.api:
        return requests.post(GCloudOCR.ENDPOINT,
                             data=GCloudOCR.format_data(image),
                             params={'key': GCloudOCR.AUTH},
                             headers=GCloudOCR.HEADERS
                             )


def in_range(value: int, min: int, max: int):
    return min <= int <= max


def debug_condition(p1: int, pc1: str, p2: int, pc2: str, p3: int):
    print("%d %s %d %s %d " % (p1, pc1, p2, pc2, p3))


def json_to_field(list):
    field_list = []
    for field in list:
        field_list.append(TextField(field, "Generic"))
    return field_list


def display_fields(image, fields, colour, show_text=False):
    bounds = None
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

def insert_record(output_csv,snumber: str, name: str) -> None:
    now = time.localtime()
    output_csv.write(
        "s%s,%s,s%s@student.rmit.edu.au,%s\n" % (snumber, name, snumber, "%.4d/%.2d/%.2d %.2d:%.2d" % (
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)))
    output_csv.flush()