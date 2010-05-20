# -*- coding: utf-8 -*-
#
# Memcache stuff for this set of webservices
# lets help make the frontend more snappy
#
from django.contrib.memcache import KeyspacedMemcacheClient
mc = KeyspacedMemcacheClient()

def memcache(basekey,kwargkeylist,timeout=120):
    def memcache_decorator(func):
        def memcache_decorated_func(request, *args, **kwargs):
            keyname = "-".join([basekey]+[str(kwargs[X]) for X in kwargkeylist])
            cached_result = mc.get(keyname)
            if cached_result:
                logger.debug("returning cached result for %s"%keyname)
                return HttpResponse(cached_result)
            
            # not cached. get real result.
            try:
                result = func(request, *args, **kwargs)
                mc.set(keyname,result,timeout)
                return HttpResponse(result)
            except ObjectDoesNotExist:
                return HttpResponseNotFound(json_error("Object not found"))
        return memcache_decorated_func
    return memcache_decorator
            
