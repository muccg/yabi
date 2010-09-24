# -*- coding: utf-8 -*-
# Create your views here.
import httplib
from urllib import urlencode, unquote, quote
import copy
import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseUnauthorized
from django.shortcuts import render_to_response, get_object_or_404, render_mako
from django.core.exceptions import ObjectDoesNotExist
from django.utils import webhelpers
from django.contrib.auth.decorators import login_required
from yabife.decorators import authentication_required
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django import forms
from django.core.servers.basehttp import FileWrapper
from django.utils import simplejson as json

from yaphc import Http, GetRequest, PostRequest, UnauthorizedError
from yaphc.memcache_persister import MemcacheCookiePersister

from django.contrib import logging
logger = logging.getLogger('yabife')

# proxy view to pass through all requests set up in urls.py
def proxy(request, url, server, base):
    logger.debug(url)
    logger.debug(server)
    logger.debug(base)
    
    target_url = os.path.join(server+base, url)
    target_request = make_request_object(target_url, request)
    return make_http_request(target_request, request.user.username, request.is_ajax())

@authentication_required
def adminproxy(request, url):
    logger.debug('')
    return proxy(request, url, settings.YABIADMIN_SERVER, settings.YABIADMIN_BASE)

# forms
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))

# views
@login_required
def files(request):
    return render_to_response('files.html', {'h':webhelpers, 'request':request})

@login_required
def design(request, id=None):
    return render_to_response('design.html', {'h':webhelpers, 'request':request, 'reuseId':id})
    
@login_required
def jobs(request):
    return render_to_response('jobs.html', {'h':webhelpers, 'request':request})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # authenticate
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    if not yabiadmin_login(username, password):
                        return render_to_response('login.html', {'h':webhelpers, 'form':form, 'error':"System error"})

                    return HttpResponseRedirect(webhelpers.url("/"))

            else:
                form = LoginForm()
                return render_to_response('login.html', {'h':webhelpers, 'form':form, 'error':"Invalid login credentials"})

        else:
            return render_to_response('login.html', {'h':webhelpers, 'form':form, 'error':"Invalid login credentials"})

    else:
        form = LoginForm()
        return render_to_response('login.html', {'h':webhelpers, 'form':form, 'url':None})


def logout(request):
    django_logout(request)
    yabiadmin_logout(request.user.username)
    return HttpResponseRedirect(webhelpers.url("/"))

# Implementation methods

def redirect_to_login():
    from django.contrib.auth import REDIRECT_FIELD_NAME
    from django.utils.http import urlquote
    #tup = settings.LOGIN_URL, REDIRECT_FIELD_NAME, urlquote(request.get_full_path())
    #return HttpResponseRedirect('%s?%s=%s' % tup)
    return HttpResponseRedirect(settings.LOGIN_URL)

def make_request_object(url, request):
    params = {}
    for k in request.REQUEST:
        params[k] = request.REQUEST[k]
    if request.method == 'GET':
        return GetRequest(url, params)
    elif request.method == 'POST':
        files = [('file%d' % (i+1), f.name, f.temporary_file_path()) for i,f in enumerate(request.FILES.values())] 
        return PostRequest(url, params, files=files)

def make_http_request(request, user, ajax_call):
    with memcache_http(user) as http:
        try:
            resp, contents = http.make_request(request)
            our_resp = HttpResponse(contents, status=int(resp.status))
            copy_non_empty_headers(resp, our_resp, ('content-disposition', 'content-type'))
            return our_resp
        except UnauthorizedError:
            if ajax_call:
                return HttpResponseUnauthorized() 
            else:
                return redirect_to_login()

def copy_non_empty_headers(src, to, header_names):
    for header_name in header_names:
        header_value = src.get(header_name)
        if header_value:
            to[header_name] = header_value

def memcache_http(username):
    mp = MemcacheCookiePersister(settings.MEMCACHE_SERVERS,
            key='%s-cookies-%s' %(settings.MEMCACHE_KEYSPACE, username))
    yabiadmin = settings.YABIADMIN_SERVER + settings.YABIADMIN_BASE
    return Http(base_url=yabiadmin, cache=False, cookie_persister=mp)

def yabiadmin_login(username, password):
    # TODO get the url from somewhere
    login_request = PostRequest('ws/login', params= {
        'username': username, 'password': password})
    http = memcache_http(username)
    resp, contents = http.make_request(login_request)
    if resp.status != 200: 
        return False
    json_resp = json.loads(contents)
    http.finish_session()
    return json_resp.get('success', False)

def yabiadmin_logout(username):
    # TODO get the url from somewhere
    logout_request = PostRequest('ws/logout')
    with memcache_http(username) as http:
        resp, contents = http.make_request(logout_request)
        if resp.status != 200: 
            return False
        json_resp = json.loads(contents)
    return json_resp.get('success', False)


