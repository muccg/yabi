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

def req_to_str(request):
    s = request.path
    for k in sorted(request.REQUEST):
        s += '-' + request.REQUEST[k]
    return s
    
def func_create_memcache_keyname(basekey, kwargs, kwargkeylist, request_specific=None, user_specific=None):
    keylist = sorted(kwargs.keys()) if kwargkeylist=='*' else kwargkeylist
    
    parts = [basekey]
    if request_specific is not None:
        parts += [req_to_str(request_specific)]
    if user_specific is not None:
        parts += [user_specific]
    parts += [str(kwargs[X]) for X in keylist]
    
    keyname = "-".join(parts)
    return keyname.encode()              # make sure its ascii if its unicode

def memcache(basekey,kwargkeylist=[],timeout=120,refresh=False,request_specific=True,user_specific=True):
    """refresh is if you want to refresh memcache with a fresh timeout on cache hit, or if you want to leave it and let it expire as per before cache hit"""
    def memcache_decorator(func):
        def memcache_decorated_func(request, *args, **kwargs):
            keyname = func_create_memcache_keyname(basekey,kwargs,kwargkeylist,request if request_specific else None, request.user.username if user_specific else None)
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


def profile_required(func):
    from yabi.models import UserProfile
    def newfunc(request,*args,**kwargs):
        # Check if the user has a profile; if not, nothing's going to work anyway,
        # so we might as well fail more spectacularly.
        try:
            request.user.get_profile()
        except ObjectDoesNotExist:
            UserProfile.objects.create(user=request.user)

        return func(request, *args, **kwargs)    
            
    return newfunc


    
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



