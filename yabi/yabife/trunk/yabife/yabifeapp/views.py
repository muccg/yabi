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
from django.contrib.auth.models import SiteProfileNotAvailable, User as DjangoUser
from django import forms
from django.core.servers.basehttp import FileWrapper
from django.utils import simplejson as json

from yaphc import Http, GetRequest, PostRequest, UnauthorizedError
from yaphc.memcache_persister import MemcacheCookiePersister

from yabife.yabifeapp.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadhandler import FileUploadHandler
from django.contrib import logging
logger = logging.getLogger('yabife')




# proxy view to pass through all requests set up in urls.py
def proxy(request, url, base):
    logger.debug(url)
    logger.debug(base)
    
    target_url = os.path.join(base, url)
    target_request = make_request_object(target_url, request)
    return make_http_request(target_request, request.user.username, request.is_ajax())

@authentication_required
def adminproxy(request, url):
    logger.debug('')
    return proxy(request, url, request.user.get_profile().appliance.url)
    
class FileUploadStreamer(from django.views.decorators.csrf import csrf_exempt

@authentication_required
@csrf_exempt
def fileupload(request, url):
    logger.debug()
    
    

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

                    # Look up the user's profile -- if they don't have one,
                    # then they don't have an appliance, and hence can't log in
                    # as such.
                    try:
                        user.get_profile()
                    except (SiteProfileNotAvailable, User.DoesNotExist):
                        return render_to_response('login.html', {'h':webhelpers, 'form':form, 'error':"User is not associated with an appliance"})

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
    username = request.user.username
    django_logout(request)
    yabiadmin_logout(username)
    return HttpResponseRedirect(webhelpers.url("/"))

def wslogin(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    username = request.POST.get('username')
    password = request.POST.get('password')
    if not (username and password):
        return HttpResponseBadRequest()
    user = authenticate(username=username, password=password)
    if user is not None: 
        if user.is_active:
            django_login(request, user)

            # Look up the user's profile -- if they don't have one, then they
            # don't have an appliance, and hence can't log in as such.
            try:
                user.get_profile()
            except (SiteProfileNotAvailable, User.DoesNotExist):
                response = {
                    "success": False,
                    "message": "User is not associated with an appliance",
                }

            if yabiadmin_login(username, password):
                response = {
                    "success": True
                }
            else:
               response = {
                    "success": False,
                    "message": "System Error (can't log in admin)",
               }
        else:
            response = {
                "success": False,
                "message": "The account has been disabled.",
            }
    else:
        response = {
            "success": False,
            "message": "The user name and password are incorrect.",
        }
    return HttpResponse(content=json.dumps(response))

def wslogout(request):
    username = request.user.username
    django_logout(request)
    yabiadmin_logout(username)
    response = {
        "success": True,
    }

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

def memcache_http(user):
    if not isinstance(user, DjangoUser):
        user = DjangoUser.objects.get(username=user)

    mp = MemcacheCookiePersister(settings.MEMCACHE_SERVERS,
            key='%s-cookies-%s' %(settings.MEMCACHE_KEYSPACE, user.username))
    yabiadmin = user.get_profile().appliance.url
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


