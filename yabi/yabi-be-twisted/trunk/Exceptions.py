# -*- coding: utf-8 -*-
"""
A set of exceptions for use throughout the backend
"""

class BlockingException(Exception):
    """Any exception derived from this instead of the normal base exception will cause
    The task manager to temporarily block rather than error out
    """
    pass

class PermissionDenied(Exception):
    """Permission denied error"""
    pass

class InvalidPath(Exception):
    """The path passed is an invalid path for this connector"""
    pass

class NoCredentials(BlockingException):
    """User has no globus credentials for this server"""
    pass

class AuthException(BlockingException):
    pass

class ProxyInitError(Exception):
    pass

class ProxyInvalidPassword(Exception):
    pass
