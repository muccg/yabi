### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
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

    def __init__(self, message="", level=SUCCESS, status=200, **kwargs):
        data = {
            "message": str(message),
            "level": level,
        }

        data.update(kwargs)
        json = dumps(data)

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
