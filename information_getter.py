import io
import json
import os

# import google as google
# import google.cloud.vision as vision_api
import time

# auth = google.discovery
from base64 import b64encode

import regex as regex
import requests


class Transcriber:
    singleton = None

    def __init__(self, target: str):
        if Transcriber.singleton is not None:
            raise Exception("We are fucked")
        Transcriber.singleton = self
        # self.v_client = vision_api.ImageAnnotatorClient()

        self.output_csv = open(str(time.time()) + "_" + target, "w+")
        self.output_csv.write("snumber,name,email,time\n")

    def interp(self, content: str) -> object:
        snumber = None
        firstname = {
            'value': None,
            'x': -1,
            'y': -1,
        }
        lastname = {
            'value': None,
            'x': -1,
            'y': -1,
        }
        full_string = []
        for annotation in content["responses"][0]["textAnnotations"]:
            if "locale" in annotation:
                continue
            text = annotation["description"]
            print(text)
            is_snumber = StudentCard.id.match(text) is not None
            is_name = StudentCard.first_name.match(text) is not None
            if text == "Expiry" or text == "Date":
                continue
            if is_snumber:
                snumber = text
            if is_name:
                firstname['value'] = text
                firstname['x'] = annotation['boundingPoly']["vertices"][0]["x"]
                firstname['y'] = annotation['boundingPoly']["vertices"][0]["y"]
        for annotation in content["responses"][0]["textAnnotations"]:
            if "locale" in annotation:
                full_string = annotation["description"].split("\n")
            text = annotation["description"]
            # print(text)
            topleft_x = annotation['boundingPoly']["vertices"][0]["x"]
            topleft_y = annotation['boundingPoly']["vertices"][0]["y"]
            if StudentCard.last_name.match(text) is None:
                # print(text + " invalid match")
                continue
            if topleft_x not in range(firstname['x'] - 10, firstname['x'] + 10):
                # print(text + " not in range")
                continue
            if abs(lastname['y'] - firstname['y']) < abs(topleft_y - firstname['y']):
                # print(text + " not closest match")
                continue
            lastname['value'] = text
            lastname['x'] = topleft_x
            lastname['y'] = topleft_y
        print(snumber)
        print(firstname['value'], lastname['value'])
        # print(full_string)
        return snumber, str(firstname['value']), str(lastname['value'])

    def do(self, path: str):
        # content = ""
        with open(path, "rb") as file:
            content = file.read()
        response = GCloudOCR.push(content)
        if response.status_code != 200:
            print("Google Down? or the internet is disconnected... choose one")
            print(response.status_code)
            print(response.content)
            return
        # image_desc = None
        # print(response.content)
        data = response.json()
        snumber, firstname, lastname = self.interp(data)
        if snumber is None or firstname is None or lastname is None:
            print("Failure: Null value")
            return
        self.insert_record(snumber, firstname + " " + lastname)

    def get_time_str(self) -> str:
        now = time.localtime()
        return "%.4d/%.2d/%.2d %.2d:%.2d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)

    def insert_record(self, snumber: str, name: str) -> None:
        self.output_csv.write("%s,%s,%s,%s\n" % ('s' + snumber, name,'s' + snumber + '@student.rmit.edu.au', self.get_time_str()))
        self.output_csv.flush()


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


class StudentCard:
    id = regex.compile('^(\d{7})$')
    first_name = regex.compile('^((?!Expiry)[A-Z][a-z\-]+)$')
    last_name = regex.compile('^([A-Z\-]+)$')
