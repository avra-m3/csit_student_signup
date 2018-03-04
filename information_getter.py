import Exceptions
from Helpers import GCloudOCR
from Types import StudentIDField, FirstNameField, LastNameField, TextField


class Card:
    def __init__(self, path_to_card: str):
        self.student_number = None
        self.names = []
        with open(path_to_card, "rb") as file:
            content = file.read()

        response = GCloudOCR.push(content)

        with open(path_to_card + ".response.json", "w+") as log_file:
            log_file.write(response.content)

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
                    raise Exceptions.UncertainMatchException()
                result = id_field
        self.student_number = result
        return result

    def get_names(self) -> [TextField]:
        if len(self.names) == 0:
            self.get_first_names()
            self.get_last_names()
        return self.names

    def get_first_names(self) -> None:
        student_number_field = self.get_student_id()
        last_result = False

        if student_number_field is None:
            return

        while last_result is not None:
            last_result = None
            for result in self.get_text_results():
                first_name_field = FirstNameField(result)
                if first_name_field.is_valid_field():
                    if last_result is False:
                        if student_number_field.is_above(first_name_field):
                            self.names.append(first_name_field)
                            last_result = first_name_field
                    else:
                        last_field = self.names[-1]
                        if last_field.is_left_of(first_name_field):
                            if last_result is not None:
                                raise Exceptions.UncertainMatchException()
                            self.names.append(first_name_field)
                            last_result = first_name_field

    def get_last_names(self) -> None:
        last_result = self.names[0]
        result_flag = True

        while not result_flag:
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

    def name_as_str(self) -> str:
        result = ""
        for name in self.names:
            result += name.get_value().capitalize()
        return result
