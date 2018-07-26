import json
from typing import List

import Exceptions
import utilities.io_functions as io
from Helpers import GCloudOCR
from Types import StudentIDField, FirstNameField, LastNameField, TextField


class Card:
    @staticmethod
    def from_json_file(file_path: str):
        """
        Constuct a Card object from a JSON file
        :param file_path: The file path to a .json file
        :return: Card() created from json
        """
        with open(file_path, "r") as f:
            j = json.load(f)
        return Card(j)

    @staticmethod
    def from_image(cfg, image: bytes):
        """
        Construct a card from a bytes image object
        :param cfg: The config.outputformat object for logging
        :param image: The bytes object of an image format google cloud accepts
        :return: Card() created from json
        Note: this function can have a long response time due to the api call it needs to make.
        """
        response = GCloudOCR.push(image)
        io.cache(cfg, response, image)
        if response.status_code == 200:
            return Card(response.json())
        return None

    @staticmethod
    def from_image_file(cfg, file_path: str):
        """
        A legacy/debugging constructor, loads an image from a file and calls from_image
        :param cfg: see from_image
        :param file_path: the file path to an image file
        :return: Card()
        """
        with open(file_path, "rb") as image:
            contents = image.read()

        return Card.from_image(cfg, contents)

    def __init__(self, json_raw: json):
        self.errors = None
        self.student_number = None
        self.json = json_raw
        self.__valid__ = []
        self.__all__ = []

        self.validate()
        if self.is_valid():
            self._populate_all()
            self._populate_student_id()
            self._populate_names()

    @property
    def student_id(self):
        return self._student_id and str(self._student_id)

    @property
    def _student_id(self):
        for field in self.fields:
            if isinstance(field, StudentIDField):
                return field

    @property
    def firstname(self):
        return " ".join([str(x).capitalize() for x in self.names if isinstance(x, FirstNameField)]) or None

    @property
    def lastname(self):
        return " ".join([str(x).capitalize() for x in self.names if isinstance(x, LastNameField)]) or None

    @property
    def names(self):
        return [x for x in self.fields if isinstance(x, LastNameField) or isinstance(x, FirstNameField)]

    @property
    def fullname(self):
        return " ".join([str(x).capitalize() for x in self.names]) or None

    @property
    def fields(self):
        return [x for x in self.__all__]

    def is_valid(self) -> bool:
        return self.errors is None

    def validate(self) -> None:
        """
        Validates the raw_json and raises an error flag if it the card information is non-retrievable
        :return: None
        """
        if "responses" not in self.json:
            self.errors = Exceptions.BadJSONResponse(json.dumps(self.json, indent=4))
        elif len(self.json["responses"]) == 0:
            self.errors = Exceptions.EmptyJSONResponse()
        elif len(self.json["responses"][0]) == 0:
            self.errors = Exceptions.EmptyJSONResponse()
        elif "textAnnotations" not in self.json["responses"][0] or len(
                self.json["responses"][0]["textAnnotations"]) < 2:
            self.errors = Exceptions.BadJSONResponse(json.dumps(self.json, indent=4))

    @property
    def __annotations__(self) -> List:
        if isinstance(self.errors, Exceptions.BadJSONResponse) or isinstance(self.errors, Exceptions.EmptyJSONResponse):
            return []
        return self.json["responses"][0]["textAnnotations"][1:]

    def _populate_all(self):
        for field in self.__annotations__:
            self.__all__.append(TextField(field, "Generic"))

    def _populate_student_id(self) -> StudentIDField:
        result = None
        result_old = None
        for field in self.fields:
            temp_field = StudentIDField(field.raw)
            if temp_field.is_valid_field():
                if result is not None:
                    raise Exceptions.UncertainMatchException("StudentID", result, temp_field)
                result = temp_field
                result_old = field
        if result is None:
            self.errors = Exceptions.NoMatchException("StudentID")
        else:
            self.__all__.remove(result_old)
            self.__all__.append(result)
        return result

    def _populate_names(self) -> None:
        """
        Populate first name fields
        :return: None
        """
        student_number_field = self._student_id
        if student_number_field is None:
            return

        valid_fields = []
        head_fields = []
        for field in self.fields:
            if field.type == "Generic":
                new_field = FirstNameField(field)
                if new_field.is_valid_field():
                    self.__all__.remove(field)
                    if student_number_field.is_above(field):
                        head_fields.append(new_field)
                    else:
                        valid_fields.append(new_field)

        if not head_fields:
            raise Exceptions.NoMatchException("First Name")

        def get_sort_order(f):
            return student_number_field.v_distance_to(f)

        head_fields.sort(key=get_sort_order)

        last_name_head = head_fields[-1]

        while head_fields:
            head = head_fields.pop(0)
            self.__all__.append(head)

            last_result = head
            flag = True

            while flag:
                flag = False
                for field in valid_fields:
                    if not last_result.adjacent_to(field):
                        continue
                    flag = True
                    self.__all__.append(field)
                    last_result = field

        """
        Last Names
        """
        valid_fields = []
        head_fields = []
        for field in self.fields:
            if type(field) == TextField:
                new_field = LastNameField(field)
                if new_field.is_valid_field():
                    self.__all__.remove(field)
                    if last_name_head.is_directly_above(field):
                        head_fields.append(new_field)
                    else:
                        valid_fields.append(new_field)

        if not head_fields:
            raise Exceptions.NoMatchException("Last Name")

        def get_sort_order(f):
            return head.v_distance_to(f)

        head_fields.sort(key=get_sort_order)

        while head_fields:
            head = head_fields.pop(0)
            self.__all__.append(head)

            last_result = head
            flag = True

            while flag:
                flag = False
                for field in valid_fields:
                    if not last_result.adjacent_to(field):
                        continue
                    flag = True
                    self.__all__.append(field)
                    last_result = field

    def get_valid_fields(self) -> List[TextField]:
        return self.__valid__
