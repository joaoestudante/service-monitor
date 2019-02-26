class CustomException(Exception):
    def __str__(self):
        return self.args[0]


class CustomRequestsException(CustomException):
    pass


class InvalidUrlException(CustomRequestsException):
    pass


class ConnectionException(CustomRequestsException):
    pass


class TimeoutException(CustomRequestsException):
    pass


class NoSchemaException(CustomRequestsException):
    pass


class BadConfigException(CustomException):
    pass


class UnrecognizedServiceException(CustomException):
    pass
