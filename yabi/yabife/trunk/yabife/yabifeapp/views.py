# Create your views here.
import httplib
from urllib import urlencode, unquote
from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, render_mako
from django.core.exceptions import ObjectDoesNotExist
from django.utils import webhelpers
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django import forms
from django.core.servers.basehttp import FileWrapper
import copy
import os

from django.contrib import logging
logger = logging.getLogger('yabife')

from yabifeapp.http_upload import *


# proxy view to pass through all requests set up in urls.py
def proxy(request, url, server, base):
    logger.debug('')
    
    #print "PROXY",request.method,repr(url),repr(server),repr(base)
    
    #if not url.startswith("/"):
        #url = "/" + url

    logger.debug(request.FILES)
    
    ## TODO CODEREVIEW
    ## Is is possible to post to a page and still send get params,
    ## are they dropped by this proxy. Would it be possible to override yabiusername by
    ## crafting a post and sending yabiusername as a get param as well

    if request.method == "GET":

        get_params = copy.copy(request.GET)
        get_params['yabiusername'] = request.user.username

        resource = "%s?%s" % (os.path.join(base, url), urlencode(get_params))
        logger.debug('Resource: %s' % resource)
        #print "Connecting to:",server
        conn = httplib.HTTPConnection(server)
        logger.debug('Server: %s' % server)        
        conn.request(request.method, resource)
        #print "%sing %r"%(request.method,resource)
        r = conn.getresponse()
        


    elif request.FILES:
        logger.debug('====================FILES====================')
        logger.debug(request.GET)
        logger.debug(request.FILES)
        logger.debug(request.GET['uri'])

        get_params = copy.copy(request.GET)
        get_params['yabiusername'] = request.user.username

        resource = "%s?%s" % (os.path.join(base, url), urlencode(get_params))

        logger.debug(resource)

        # TODO this only works with files written to disk by django
        # at the moment so the FILE_UPLOAD_MAX_MEMORY_SIZE must be set to 0
        # in settings.py
        files = []
        in_file = request.FILES['file1']
        files.append(('file1', in_file.name, in_file.temporary_file_path()))
        h = post_multipart(server, resource, [], files)
        logger.debug(in_file.temporary_file_path())
        r = h.getresponse()
        

    elif request.method == "POST":

        resource = os.path.join(base, url)
        logger.debug('Resource: %s' % resource)

        post_params = copy.copy(request.POST)
        post_params['yabiusername'] = request.user.username

        data = urlencode(post_params)
        logger.debug('Data: %s' % data)
        headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
        conn = httplib.HTTPConnection(server)
        #print "Connecting to:",server
        logger.debug('Server: %s' % server)
        conn.request(request.method, resource, data, headers)
        #print "%sing %r with data %s and headers %s"%(request.method,resource,data,headers)
        r = conn.getresponse()

    #print "returning response:",r.status
    response = HttpResponse(r.read(), status=int(r.status))

    if r.getheader('content-disposition', None):
        response['content-disposition'] = r.getheader('content-disposition')

    if r.getheader('content-type', None):
        response['content-type'] = r.getheader('content-type')

    return response


def adminproxy(request, url):
    logger.debug('')
    return proxy(request, url, settings.YABIADMIN_SERVER, settings.YABIADMIN_BASE)
    

def storeproxy(request, url):
    logger.debug('')
    return proxy(request, url, settings.YABISTORE_SERVER, settings.YABISTORE_BASE)


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
        return render_to_response('login.html', {'h':webhelpers, 'form':form})


def logout(request):
    django_logout(request)
    return HttpResponseRedirect(webhelpers.url("/"))


