# -*- coding: utf-8 -*-
import httplib
from urllib import urlencode, unquote, quote
import copy
import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, render_mako
from django.core.exceptions import ObjectDoesNotExist
from django.utils import webhelpers
from django import forms

from django.contrib import logging
logger = logging.getLogger('yabiadmin')

# proxy view to pass through all requests set up in urls.py
def proxy(request, url, server, base):
    logger.debug(url)
    logger.debug(server)
    logger.debug(base)
    
    ## TODO CODEREVIEW
    ## Is is possible to post to a page and still send get params,
    ## are they dropped by this proxy. Would it be possible to override yabiusername by
    ## crafting a post and sending yabiusername as a get param as well

    if request.method == "GET":
        #resource = "%s?%s" % (os.path.join(base, url), request.META['QUERY_STRING']+"&yabiusername=%s"%quote(request.user.username) )
        resource = "%s?%s" % (os.path.join(base, url), request.META['QUERY_STRING']) 
        logger.debug('Proxying get: %s%s' % (server, resource))
        conn = httplib.HTTPConnection(server)
        conn.request(request.method, resource)
        r = conn.getresponse()

    elif request.method == "POST":
        resource = os.path.join(base, url)
        post_params = copy.copy(request.POST)
        #post_params['yabiusername'] = request.user.username
        logger.debug('Proxying post: %s%s' % (server, resource))
        data = urlencode(post_params)
        headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
        conn = httplib.HTTPConnection(server)
        conn.request(request.method, resource, data, headers)
        r = conn.getresponse()

    data = r.read()
    response = HttpResponse(data, status=int(r.status))

    if r.getheader('content-disposition', None):
        response['content-disposition'] = r.getheader('content-disposition')

    if r.getheader('content-type', None):
        response['content-type'] = r.getheader('content-type')

    return response

from decorators import memcache

@memcache("store",timeout=30)
def storeproxy(request, url):
    logger.debug('')
    assert request.method=="GET"
    return proxy(request, url, settings.YABISTORE_SERVER, settings.YABISTORE_BASE)
