# -*- coding: utf-8 -*-
#
# Memcache stuff for this set of webservices
# lets help make the frontend more snappy
#
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseUnauthorized

import logging
logger = logging.getLogger('yabiadmin')

from django.contrib.memcache import KeyspacedMemcacheClient
mc = KeyspacedMemcacheClient()

import pickle

def req_to_str(request, user_specific):
    s = request.path
    if user_specific:
        s += '-' + request.user.username
    for k in sorted(request.REQUEST):
        s += '-' + request.REQUEST[k]
    return s

def memcache(basekey,kwargkeylist=[],timeout=120,refresh=False,user_specific=True):
    """refresh is if you want to refresh memcache with a fresh timeout on cache hit, or if you want to leave it and let it expire as per before cache hit"""
    def memcache_decorator(func):
        def memcache_decorated_func(request, *args, **kwargs):
            keylist = sorted(kwargs.keys()) if kwargkeylist=='*' else kwargkeylist
            keyname = "-".join([basekey, req_to_str(request,user_specific)] + [str(kwargs[X]) for X in keylist])
            keyname = keyname.encode()
            cached_result = mc.get(keyname)
            if cached_result:
                if refresh:
                    logger.debug("updating cached timestamp for %s"%keyname)
                    mc.set(keyname,cached_result,timeout)
                logger.debug("returning cached result for %s"%keyname)
                return pickle.loads(cached_result)
            
            # not cached. get real result.
            logger.debug("result not cached... caching %s"%keyname)
            result = func(request, *args, **kwargs)
            mc.set(keyname,pickle.dumps(result),timeout)
            return result
        return memcache_decorated_func
    return memcache_decorator
            

def authentication_required(f):
    """
    This decorator is used instead of the django login_required decorator
    because we return HttpResponseUnauthorized while Django's redirects to
    the login page.
    """
    def new_function(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()
        return f(*args, **kwargs)
    return new_function
    
# Number of times to indent output
# A list is used to force access by reference
__report_indent = [0]

def report(fn):
    """Decorator to print information about a function
    call for use while debugging.
    Prints function name, arguments, and call number
    when the function is called. Prints this information
    again along with the return value when the function
    returns.
    """

    def wrap(*params,**kwargs):
        call = wrap.callcount = wrap.callcount + 1

        indent = ' ' * __report_indent[0]
        fc = "%s(%s)" % (fn.__name__, ', '.join(
            [a.__repr__() for a in params] +
            ["%s = %s" % (a, repr(b)) for a,b in kwargs.items()]
        ))

        print "CALL: %s%s [#%s]" % (indent, fc, call)
        __report_indent[0] += 1
        ret = fn(*params,**kwargs)
        __report_indent[0] -= 1
        print "RETURN: %s%s %s [#%s]" % (indent, fc, repr(ret), call)

        return ret
    wrap.callcount = 0
    return wrap    
