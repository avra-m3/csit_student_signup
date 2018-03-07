class InvalidResponseException(IndexError):
    pass


class BadObjectCreationException(RuntimeError):
    pass

class UncertainMatchException(Exception):
    pass

class NoMatchException(Exception):
    pass