import io
import os
import google.cloud.vision as vision_api


class Transcriber:
    def __init__(self, target: str):
        self.v_client = vision_api.ImageAnnotatorClient()
        self.output_csv = open(target, "w")

    def do(self, content: str):
        image = vision_api.types.Image(content=content)
        image_content = self.v_client.label_detection(image=image)
        for line in image_content:
            print(line.description)
            print(line.__dict__)


single_transcriber = Transcriber('output.csv')
with open('WIN_20180225_11_34_05_Pro.jpg', 'r+') as image_file:
    image_str = image_file.read()
single_transcriber.do(image_str)
