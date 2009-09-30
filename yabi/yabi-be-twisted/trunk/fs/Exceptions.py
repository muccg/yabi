"""This file contains all the exceptions raised by problems encountered by the filesystem connectors
"""

class PermissionDenied(Exception):
    """Permission denied error"""
    pass

class InvalidPath(Exception):
    """The path passed is an invalid path for this connector"""
    pass


