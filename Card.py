import json
from typing import List

import Exceptions
from Helpers import GCloudOCR
from Types import StudentIDField, FirstNameField, LastNameField, TextField


class Card:
    def __init__(self, path_to_image: str = None, path_to_json: str = None):

        self.student_number = None
        self.names = []
        self.ocr_result = None

        if path_to_image is not None:
            self.from_image(path_to_image)
        elif path_to_json is not None:
            self.from_json(path_to_json)
        else:
            raise RuntimeWarning

    def from_json(self, path_to_json):
        with open(path_to_json, 'r') as file:
            self.ocr_result = json.load(file)

    def from_image(self, path_to_image):
        with open(path_to_image, "rb") as file:
            content = file.read()

        response = GCloudOCR.push(content)

        with open(path_to_image + ".response.json", "wb") as log_file:
            log_file.write(response.content)
            log_file.flush()
            # print(response.content)

        if response.status_code == 200:
            self.ocr_result = response.json()
        else:
            raise Exceptions.InvalidResponseException(response.content)

    def get_text_results(self) -> list:
        return self.ocr_result["responses"][0]["textAnnotations"][1:]

    def get_student_id(self) -> StudentIDField:
        if self.student_number is not None:
            return self.student_number

        result = None
        for text_result in self.get_text_results():
            id_field = StudentIDField(text_result)
            if id_field.is_valid_field():
                if result is not None:
                    # print(result)
                    raise Exceptions.UncertainMatchException()
                result = id_field
        if result is None:
            raise Exceptions.NoMatchException
        self.student_number = result
        return result

    def get_names(self) -> List[TextField]:
        if len(self.names) == 0:
            self.get_first_names()
            self.get_last_names()
        return self.names

    def get_first_names(self) -> None:
        student_number_field = self.get_student_id()
        last_result = student_number_field

        result_flag = True

        while result_flag:
            result_flag = False
            for result in self.get_text_results():
                first_name_field = FirstNameField(result)
                if first_name_field.is_valid_field():
                    if type(last_result) is StudentIDField:
                        if student_number_field.is_below(first_name_field):
                            self.names.append(first_name_field)
                            last_result = first_name_field
                            result_flag = True
                    else:
                        last_field = self.names[-1]
                        if last_field.is_left_of(first_name_field):
                            self.names.append(first_name_field)
                            last_result = first_name_field
                            result_flag = True
        if type(last_result) is StudentIDField:
            raise Exceptions.NoMatchException()

    def get_last_names(self) -> None:
        last_result = self.names[0]
        result_flag = True

        while result_flag:
            result_flag = False
            for result in self.get_text_results():
                last_name_field = LastNameField(result)
                if last_name_field.is_valid_field():
                    if type(last_result) is FirstNameField:
                        if last_result.is_above(last_name_field):
                            self.names.append(last_name_field)
                            last_result = last_name_field
                            result_flag = True

                    else:
                        if last_result.is_left_of(last_name_field):
                            self.names.append(last_name_field)
                            last_result = last_name_field
                            result_flag = True
        if type(last_result) is FirstNameField:
            raise Exceptions.NoMatchException()

    def name_as_str(self) -> str:
        return " ".join(map(lambda x: x.get_value().capitalize(), self.get_names()))
