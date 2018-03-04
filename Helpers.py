import json
import os
from base64 import b64encode

import regex as regex
import requests


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
