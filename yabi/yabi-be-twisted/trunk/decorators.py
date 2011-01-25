# -*- coding: utf-8 -*-
import stackless
from utils.stacklesstools import sleep

DEFAULT_FUNCTION_RETRY = 3

def default_delay_generator():
    delay = 5.0
    while True:
        yield delay
        delay *= 2.0
    
def retry(num_retries = DEFAULT_FUNCTION_RETRY, ignored=[], delay_func = None):
    """num_retries is how often to retry the function.
    ignored is a list of exception classes to ignore (allow to fall through and fail the function so it doesnt retry)
    delay_func is a generator function to produce the delay generator
    """
    def retry_decorator(f):
        def new_func(*args, **kwargs):
            num = num_retries
            if delay_func:
                gen = delay_func()
            else:
                gen = default_delay_generator()
            while True:
                try:
                    return f(*args, **kwargs)               # exits on success
                except Exception, exc:
                    if True in [isinstance(exc,E) for E in ignored]:                # is this an exception we should ignore
                        raise                                                       # raise the exception
                    if num:
                        delay = gen.next()
                        print "WARNING: retry-function",f,"raised exception",exc,"... waiting",delay,"seconds and retrying",num,"more times..."
                        sleep(delay)
                        num -= 1
                    else:
                        raise                               # out of retries... fail
        return new_func
    return retry_decorator

def lock(maximum):
    def lock_decorator(f):
        if not hasattr(f,'_CONNECTION_COUNT'):
            f._CONNECTION_COUNT = 0
        def new_func(*args, **kwargs):
            
            # pre lock
            while f._CONNECTION_COUNT >= maximum:
                print "WARNING: max connection count reached for",f,"(%d)"%maximum
                stackless.schedule()
                
            f._CONNECTION_COUNT += 1
            
            try:
                return f(*args, **kwargs)
            finally:
                # post lock
                f._CONNECTION_COUNT -= 1
                
        return new_func
    return lock_decorator
    
def call_count(f):
    if not hasattr(f,'_CONNECTION_COUNT'):
        f._CONNECTION_COUNT = 0
    def new_func(*args, **kwargs):
        f._CONNECTION_COUNT += 1
        print "function",f,f.__name__,"has",f._CONNECTION_COUNT,"present callees"
        try:
            return f(*args, **kwargs)
        finally:
            # post lock
            f._CONNECTION_COUNT -= 1
    return new_func

