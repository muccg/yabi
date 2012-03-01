# -*- coding: utf-8 -*-
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
# -*- coding: utf-8 -*-
import stackless
from utils.stacklesstools import sleep

DEFAULT_FUNCTION_RETRY = 3

def default_delay_generator():
    delay = 5.0
    while delay<300.:
        yield delay
        delay *= 2.0
    while True:
        yield 300.          # five minutes forever more
    
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

def timed_retry(total_time=600.,ignored=[]):
    def timed_retry_decorator(f):
        def new_func(*args, **kwargs):
            time_waited = 0.
            gen = default_delay_generator()
            while time_waited<total_time:
                try:
                    return f(*args, **kwargs)               # exits on success
                except Exception, exc:
                    if True in [isinstance(exc,E) for E in ignored]:                # is this an exception we should ignore
                        raise                                                       # raise the exception
                    
                    if time_waited<total_time:
                        delay = gen.next()
                        print "WARNING: retry-function",f,"raised exception",exc,"... waiting",delay,"seconds and retrying..."
                        sleep(delay)
                    else:
                        raise                               # out of retries... fail
                        
        return new_func
    return timed_retry_decorator    
    
from conf import config

def conf_retry(ignored=[]):
    return timed_retry(config.config["taskmanager"]["retrywindow"], ignored)

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

from twistedweb2 import http, responsecode, http_headers
import hmac
from conf import config

#
# for resources that need to be authed via hmac secret
#
def hmac_authenticated(func):
    def newfunc(self, request, *args, **kwargs):
        # check hmac result
        headers = request.headers
        if not headers.hasHeader("hmac-digest"):
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "No hmac-digest header present in http request.\n")
            
        digest_incoming = headers.getRawHeaders("hmac-digest")[0]
        uri = request.uri
        
        hmac_digest = hmac.new(config.config['backend']['hmackey'])
        hmac_digest.update(uri)
        
        if hmac_digest.hexdigest() != digest_incoming:
            return http.Response( responsecode.UNAUTHORIZED, {'content-type': http_headers.MimeType('text', 'plain')}, "hmac-digest header present in http request is incorrect.\n")
        
        return func(self,request, *args, **kwargs)
    return newfunc
    
