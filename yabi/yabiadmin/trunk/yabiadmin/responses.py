from django.http import HttpResponse
from json import dumps


# Constants.
SUCCESS = "success"
WARNING = WARN = "warn"
ERROR = FAIL = "fail"


class JsonMessageResponse(HttpResponse):
    """
    A class representing a JSON response in the standard format used for YABI
    Web services that don't need to return anything other than a simple message
    to be displayed to the user.
    """

    def __init__(self, message="", level=SUCCESS, status=200):
        json = dumps({
            "message": str(message),
            "level": level,
        })

        super(JsonMessageResponse, self).__init__(content=json, content_type="application/json; charset=UTF-8", status=status)


class JsonMessageResponseBadRequest(JsonMessageResponse):
    def __init__(self, message="", level=FAIL, status=400):
        super(JsonMessageResponseBadRequest, self).__init__(message=message, level=level, status=status)


class JsonMessageResponseNotFound(JsonMessageResponse):
    def __init__(self, message="", level=FAIL, status=404):
        super(JsonMessageResponseNotFound, self).__init__(message=message, level=level, status=status)


class JsonMessageResponseForbidden(JsonMessageResponse):
    def __init__(self, message="", level=FAIL, status=403):
        super(JsonMessageResponseForbidden, self).__init__(message=message, level=level, status=status)


class JsonMessageResponseGone(JsonMessageResponse):
    def __init__(self, message="", level=FAIL, status=410):
        super(JsonMessageResponseGone, self).__init__(message=message, level=level, status=status)


class JsonMessageResponseServerError(JsonMessageResponse):
    def __init__(self, message="", level=FAIL, status=500):
        super(JsonMessageResponseServerError, self).__init__(message=message, level=level, status=status)


class JsonMessageResponseNotAllowed(JsonMessageResponse):
    def __init__(self, allowed, message="Request method not supported", level=FAIL, status=405):
        super(JsonMessageResponseNotAllowed, self).__init__(message=message, level=level, status=status)
        self["Allow"] = ", ".join(allowed)
