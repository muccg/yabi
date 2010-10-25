"""
A set of exceptions for use throughout the backend
"""

class BlockingException(Exception):
    """Any exception derived from this instead of the normal base exception will cause
    The task manager to temporarily block rather than error out
    """
    pass

