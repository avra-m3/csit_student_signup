import json

# from Types import TextField


class BadBoundingException(Exception):
    STR_MESSAGE = "One or more bounding boxes returned by third party client contained errors"

    def __init__(self, invalid_field: json):
        super().__init__({
            "message": self.STR_MESSAGE,
            "error values": invalid_field
        })


class BadRequestResponse(Exception):
    STR_MESSAGE = "Third party client returned a response indicating an error"

    def __init__(self, status_code: int, content: json):
        super().__init__({
            "message": self.STR_MESSAGE,
            "error values": status_code,
            "error content": content
        })


class UncertainMatchException(Exception):
    STR_MESSAGE = "Found 2 or more fields matching the parameters expected of field: %s"

    def __init__(self, field_name: str, param1, param2):
        super().__init__(
            {"message": self.STR_MESSAGE % field_name,
             "error values": [param1, param2]
             }
        )


class NoMatchException(Exception):
    STR_MESSAGE = "Could not find a field matching the parameter"

    def __init__(self, field_name: str):
        super().__init__({
            "message": self.STR_MESSAGE,
            "error values": field_name
        })
