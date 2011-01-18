# -*- coding: utf-8 -*-
import stackless

DEFAULT_FUNCTION_RETRY = 3

def default_delay_generator():
    delay = 10.0
    while delay<60.0:
        yield delay
        delay *= 2.0
    while True:
        yield delay
    
def retry(num_retries = DEFAULT_FUNCTION_RETRY, delay_func = None):
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
                except Exception, E:
                    if num:
                        delay = gen.next()
                        print "WARNING: retry-function",f,"raised exception",E,"... waiting",delay,"seconds and retrying",num,"more times..."
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
    
    