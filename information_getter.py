import time

import os

from Helpers import GCloudOCR, StudentCard

import Exceptions
from Types import TextField
from config import Config


class Transcriber:
    singleton = None

    def __init__(self, target: str):
        if Transcriber.singleton is not None:
            raise Exceptions.BadObjectCreationException()
        Transcriber.singleton = self

        if not os.path.exists(target):
            self.output_csv = open(target, "w")
            self.output_csv.write("snumber,name,email,time\n")
        elif os.path.isfile(target):
            self.output_csv = open(target, 'a')

    def find_snumber(self, content) -> TextField:
        result = None

        for annotation in content["responses"][0]["textAnnotations"]:
            if "locale" in annotation:
                continue
            temp = TextField(annotation)
            if StudentCard.id.match(temp.value) is not None:
                if result is not None:
                    raise Exceptions.UncertainMatchException()
                result = temp
        return result


    def find_first_name(self, content, snumber: TextField) -> [TextField]:
        names = []
        name_count = 0
        end_flag = False
        while end_flag != False:
            end_flag = True
            for annotation in content["responses"][0]["textAnnotations"]:
                if "locale" in annotation:
                    continue
                temp = TextField(annotation)
                if name_count == 0:
                    if snumber.bounds.bl()['x']-Config.word_gap <= temp.bounds.tl()['x'] <= snumber.bounds.bl()['x']+Config.word_gap  and \
                        snumber.bounds.bl('y') <= temp.bounds.tl(['y']) <= snumber.bounds.bl()['y']+Config.word_gap*2:
                        if len(names) != name_count:
                            raise Exceptions.UncertainMatchException()
                        names.append(temp)
                        end_flag = False
                else:
                    last_bounds = names[name_count].bounds
                    if last_bounds.tr('x') <= temp.bounds.tl('x') <= last_bounds.tr('x') +Config.word_gap  and \
                        last_bounds.tr('y') - Config.word_gap/2 <= temp.bounds.tl('y') <= last_bounds.tr('y') + Config.word_gap/2 and\
                        last_bounds.br('y') - Config.word_gap/2 <= temp.bounds.bl('y') <= last_bounds.br('y') + Config.word_gap/2:
                        if len(names) != name_count:
                            raise Exceptions.UncertainMatchException()
                        names.append(temp)
                        end_flag = False
            name_count += end_flag







    def interp(self, content: str) -> object:
        snumber =
        firstname = {
            'values': None,
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
            print("Google Down? or the internet is disconnected... who knows?")
            print(response.status_code)
            print(response.content)
            return
        # image_desc = None
        # print(response.content)
        data = response.json()
        snumber, firstname, lastname = self.interp(data)
        if snumber is None or firstname is None or lastname is None:
            print("Failure: Null value")
            return data
        self.insert_record(snumber, firstname + " " + lastname)
        return data

    def get_time_str(self) -> str:
        now = time.localtime()
        return "%.4d/%.2d/%.2d %.2d:%.2d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)

    def insert_record(self, snumber: str, name: str) -> None:
        self.output_csv.write(
            "%s,%s,%s,%s\n" % ('s' + snumber, name, 's' + snumber + '@student.rmit.edu.au', self.get_time_str()))
        self.output_csv.flush()
