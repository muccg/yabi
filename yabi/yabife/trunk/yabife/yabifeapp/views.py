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
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, render_mako
from django.core.exceptions import ObjectDoesNotExist
from django.utils import webhelpers
from django.contrib.auth.decorators import login_required
from yabife.decorators import authentication_required
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django import forms
from django.core.servers.basehttp import FileWrapper

from django.contrib import logging
logger = logging.getLogger('yabife')

from yabifeapp.http_upload import *

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
        resource = "%s?%s" % (os.path.join(base, url), request.META['QUERY_STRING']+"&yabiusername=%s"%quote(request.user.username) )
        logger.debug('Proxying get: %s%s' % (server, resource))
        conn = httplib.HTTPConnection(server)
        conn.request(request.method, resource)
        r = conn.getresponse()

    elif request.FILES:
        get_params = copy.copy(request.GET)
        get_params['yabiusername'] = request.user.username
        resource = "%s?%s" % (os.path.join(base, url), urlencode(get_params))

        # TODO this only works with files written to disk by django
        # at the moment so the FILE_UPLOAD_MAX_MEMORY_SIZE must be set to 0
        # in settings.py
        files = []
        in_file = request.FILES['file1']
        logger.debug('Proxying file: %s to %s%s' % (in_file.temporary_file_path(), server, resource))
        files.append(('file1', in_file.name, open(in_file.temporary_file_path())))
        h = post_multipart(server, resource, [], files)
        r = h.getresponse()

    elif request.method == "POST":
        resource = os.path.join(base, url)
        post_params = copy.copy(request.POST)
        post_params['yabiusername'] = request.user.username
        logger.debug('Proxying post: %s%s' % (server, resource))
        data = urlencode(post_params)
        headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
        conn = httplib.HTTPConnection(server)
        conn.request(request.method, resource, data, headers)
        r = conn.getresponse()

    data = r.read()
    response = HttpResponse(data, status=int(r.status))

    #logger.debug("Got %d bytes returned with status code %d. First part of data is: %s"%(len(data),r.status,data[:64 if len(data)<64 else len(data)]))

    if r.getheader('content-disposition', None):
        response['content-disposition'] = r.getheader('content-disposition')

    if r.getheader('content-type', None):
        response['content-type'] = r.getheader('content-type')

    return response


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
    return HttpResponseRedirect(webhelpers.url("/"))


