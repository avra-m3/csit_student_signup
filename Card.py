import json
from typing import List

import Exceptions
import utilities.io_functions as io
from Helpers import GCloudOCR
from Types import StudentIDField, FirstNameField, LastNameField, TextField


class Card:
    @staticmethod
    def from_json_file(cfg, file_path: str):
        with open(file_path, "r") as f:
            j = json.load(f)
        return Card(j)

    @staticmethod
    def from_image_file(cfg, file_path: str):
        with open(file_path, "rb") as image:
            contents = image.read()

        return Card.from_image(cfg, contents)

    @staticmethod
    def from_image(cfg, image: bytes):
        response = GCloudOCR.push(image)
        io.cache(cfg, response, image)
        if response.status_code == 200:
            return Card(response.json())
        return None

    def __init__(self, json: json):

        self.errors = None
        self.student_number = None
        self.names = []
        self.json = json
        self.__valid__ = []
        self.__all__ = []

        self.validate_json()

    def is_valid(self) -> bool:
        return self.errors is None

    def validate_json(self) -> None:
        if "responses" not in self.json:
            self.errors = Exceptions.BadJSONResponse(json.dumps(self.json, indent=4))
        elif len(self.json["responses"]) == 0:
            self.errors = Exceptions.EmptyJSONResponse()
        elif len(self.json["responses"][0]) == 0:
            self.errors = Exceptions.EmptyJSONResponse()
        elif "textAnnotations" not in self.json["responses"][0] or len(
                self.json["responses"][0]["textAnnotations"]) < 2:
            self.errors = Exceptions.BadJSONResponse(json.dumps(self.json, indent=4))

    def get_annotations(self) -> List:
        if isinstance(self.errors, Exceptions.BadJSONResponse) or isinstance(self.errors, Exceptions.EmptyJSONResponse):
            return []
        return self.json["responses"][0]["textAnnotations"][1:]

    def get_field_results(self) -> List[TextField]:
        if self.is_valid() or not isinstance(self.errors, Exceptions.BadJSONResponse):
            if len(self.__all__) == 0:
                for field in self.get_annotations():
                    self.__all__.append(TextField(field, "Generic"))
            return self.__all__
        else:
            return []

    def get_student_id(self) -> StudentIDField:
        if self.student_number is not None:
            return self.student_number
        if self.is_valid():
            result = None
            for text_result in self.get_annotations():
                id_field = StudentIDField(text_result)
                if id_field.is_valid_field():
                    if result is not None:
                        raise Exceptions.UncertainMatchException("StudentID", result, id_field)
                    result = id_field
            if result is None:
                self.errors = Exceptions.NoMatchException("StudentID")
            else:
                self.__valid__.append(result)
            self.student_number = result
            return result

    def get_names(self) -> List[TextField]:
        if self.is_valid() and len(self.names) == 0:
            self.get_first_names()
            self.get_last_names()
        return self.names

    def get_first_names(self) -> None:
        student_number_field = self.get_student_id()
        last_result = student_number_field

        result_flag = True
        if self.is_valid():
            while result_flag:
                result_flag = False
                for result in self.get_annotations():
                    first_name_field = FirstNameField(result)
                    if first_name_field.is_valid_field():
                        if type(last_result) is StudentIDField:
                            if student_number_field.is_below(first_name_field):
                                self.names.append(first_name_field)
                                self.__valid__.append(first_name_field)
                                last_result = first_name_field
                                result_flag = True
                        else:
                            last_field = self.names[-1]
                            if last_field.is_left_of(first_name_field):
                                self.names.append(first_name_field)
                                self.__valid__.append(first_name_field)
                                last_result = first_name_field
                                result_flag = True
            if type(last_result) is StudentIDField:
                self.errors = Exceptions.NoMatchException("First Name")

    def get_last_names(self) -> None:
        last_result = self.names[0]
        result_flag = True
        if self.is_valid():
            while result_flag:
                result_flag = False
                for result in self.get_annotations():
                    last_name_field = LastNameField(result)
                    if last_name_field.is_valid_field():
                        if type(last_result) is FirstNameField:
                            if last_result.is_above(last_name_field):
                                self.names.append(last_name_field)
                                self.__valid__.append(last_name_field)
                                last_result = last_name_field
                                result_flag = True

                        else:
                            if last_result.is_left_of(last_name_field):
                                self.names.append(last_name_field)
                                self.__valid__.append(last_name_field)
                                last_result = last_name_field
                                result_flag = True
            if type(last_result) is FirstNameField:
                self.errors = Exceptions.NoMatchException("Last Name")

    def get_valid_fields(self) -> List[TextField]:
        return self.__valid__

    def get_name(self) -> str:
        return " ".join(map(lambda x: x.get_value().capitalize(), self.get_names()))
