# -*- coding: utf-8 -*-
#
# Memcache stuff for this set of webservices
# lets help make the frontend more snappy
#
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound

import logging
logger = logging.getLogger('yabiadmin')

from django.contrib.memcache import KeyspacedMemcacheClient
mc = KeyspacedMemcacheClient()

import pickle

def memcache(basekey,kwargkeylist,timeout=120,refresh=True):
    """refresh is if you want to refresh memcache with a fresh timeout on cache hit, or if you want to leave it and let it expire as per before cache hit"""
    def memcache_decorator(func):
        def memcache_decorated_func(request, *args, **kwargs):
            keyname = "-".join([basekey]+[str(kwargs[X]) for X in kwargkeylist])
            cached_result = mc.get(keyname)
            if cached_result:
                if refresh:
                    logger.debug("updating cached timestamp")
                    mc.set(keyname,cached_result,timeout)
                logger.debug("returning cached result for %s"%keyname)
                return pickle.loads(cached_result)
            
            # not cached. get real result.
            result = func(request, *args, **kwargs)
            mc.set(keyname,pickle.dumps(result),timeout)
            return result
        return memcache_decorated_func
    return memcache_decorator
            