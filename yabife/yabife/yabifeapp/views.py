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

import httplib
from urllib import urlencode, unquote, quote
import copy
from email.utils import formatdate
import datetime
import hashlib
import os
from time import mktime
from urlparse import urlparse

from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from ccg.http import HttpResponseUnauthorized
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.utils import webhelpers
from django.contrib.auth.decorators import login_required
from yabife.decorators import authentication_required, profile_required
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django.contrib.auth.models import SiteProfileNotAvailable, User as DjangoUser
from django.contrib.sessions.models import Session
from django import forms
from django.core.servers.basehttp import FileWrapper
from django.template.loader import get_template
from django.utils import simplejson as json
from django.utils.importlib import import_module

from yaphc import Http, GetRequest, PostRequest, UnauthorizedError
from yaphc.memcache_persister import MemcacheCookiePersister

from yabife.yabifeapp.models import User
from yabife.responses import *
from yabife.preview import html

from utils import memcache_client, memcache_http, make_http_request, make_request_object, preview_key, yabiadmin_passchange, logout, yabiadmin_logout

import logging
logger = logging.getLogger(__name__)

from UploadStreamer import UploadStreamer
from django.views.decorators.csrf import csrf_exempt

class FileUploadStreamer(UploadStreamer):
    def __init__(self, host, port, selector, cookies, fields):
        UploadStreamer.__init__(self)
        self._host = host
        self._port = port
        self._selector = selector
        self._fields = fields
        self._cookies = cookies
    
    def receive_data_chunk(self, raw_data, start):
        #print "receive_data_chunk", len(raw_data), start
        return self.file_data(raw_data)
    
    def file_complete(self, file_size):
        """individual file upload complete"""
        #print "file_complete",file_size
        return self.end_file()
    
    def new_file(self, field_name, file_name, content_type, content_length, charset):
        """beginning of new file in upload"""
        #print "new_file",field_name, file_name, content_type, content_length, charset
        return UploadStreamer.new_file(self,file_name)
    
    def upload_complete(self):
        """all files completely uploaded"""
        #print "upload_complete"
        return self.end_connection()
    
    def handle_raw_input(self, input_data, META, content_length, boundary, encoding, chunked):
        """raw input"""
        # this is called right at the beginning. So we grab the uri detail here and initialise the outgoing POST
        self.post_multipart(host=self._host, port=self._port, selector=self._selector, cookies=self._cookies )
        
@authentication_required
def fileupload(request, url):
    return upload_file(request, request.user)

def fileupload_session(request, url, session):
    def response(message, level=ERROR, status=500):
        return HttpResponse(status=status, content=json.dumps({
            "level": level,
            "message": message,
        }))

    # Get the user out of the session. Annoyingly, we'll have to do our own
    # session handling here.
    try:
        session = Session.objects.get(pk=session)
        
        # Check expiry date.
        if session.expire_date < datetime.datetime.now():
            return response("Session expired")

        # Get the user, if set.
        request.user = user = DjangoUser.objects.get(pk=session.get_decoded()["_auth_user_id"])

        # Update the session object in the request.
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore(session.pk)
    except DjangoUser.DoesNotExist:
        return response("User not found", status=403)
    except KeyError:
        return response("User not logged in", status=403)
    except Session.DoesNotExist:
        return response("Unable to read session")

    return upload_file(request, user)
    
# proxy view to pass through all requests set up in urls.py
def proxy(request, url, base):
    logger.debug(url)
    logger.debug(base)
    
    target_url = os.path.join(base, url)
    target_request = make_request_object(target_url, request)
    return make_http_request(target_request, request, request.is_ajax())

@authentication_required
@profile_required
def adminproxy(request, url):
    logger.debug('')
    return proxy(request, quote(url), settings.YABIADMIN_SERVER)

@authentication_required
def adminproxy_cache(request, url):
    response = adminproxy(request, url)

    expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
    response["Expires"] = formatdate(timeval=mktime(expiry.timetuple()), usegmt=True)

    return response

# forms
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))

# views
def render_page(template, request, response=None, **kwargs):
    if not response:
        response = HttpResponse()

    # Check for the debug cookie or GET variable.
    debug = False

    if request.COOKIES.get("yabife-debug"):
        debug = True
    elif request.GET.get("yabife-debug"):
        debug = True
        response.set_cookie("yabife-debug", "1", path=webhelpers.url("/"))

    # Actually render the template.
    context = {
        "h": webhelpers,
        "request": request,
        "debug": debug,
    }
    context.update(kwargs)
    return render_to_response(template, context)


@login_required
@profile_required
def files(request):
    return render_page("files.html", request)

@login_required
@profile_required
def design(request, id=None):
    return render_page("design.html", request, reuseId=id)
    
@login_required
@profile_required
def jobs(request):
    return render_page("jobs.html", request)

@login_required
@profile_required
def account(request):
    if not request.user.get_profile().has_account_tab():
        return render_page("errors/403.html", request, response=HttpResponseForbidden())
    return render_page("account.html", request)

def login(request):
    logger.error('')
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
                    yabiadmin_login(request, username, password)

                    # TODO need to be able to get this message to frontend, not so easily done using decorator
                    # but don't want to duplicate decorator code here just to get this message in
                    #  success, message = yabiadmin_login(request, username, password)
                    # if not success:
                    #     return render_to_response('login.html', {'h':webhelpers, 'form':form, 'error':message})

                    return HttpResponseRedirect(webhelpers.url("/"))

            else:
                form = LoginForm()
                return render_to_response('login.html', {'h':webhelpers, 'form':form, 'error':"Invalid login credentials"})

        else:
            return render_to_response('login.html', {'h':webhelpers, 'form':form, 'error':"Invalid login credentials"})

    else:
        form = LoginForm()
        error = request.GET['error'] if 'error' in request.GET else ''
        return render_to_response('login.html', {'h':webhelpers, 'form':form, 'url':None, 'error':error})



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

            yabiadmin_login(request, username, password)
            response = {
                "success": True
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
    yabiadmin_logout(request)
    django_logout(request)
    response = {
        "success": True,
    }
    return HttpResponse(content=json.dumps(response))

@authentication_required
def credentialproxy(request, url):
    try:
        if request.user.get_profile().credential_access:
            return adminproxy(request, url)
    except ObjectDoesNotExist:
        mail_admins_no_profile(request.user)
        return JsonMessageResponseUnauthorized("User does not have a profile or user record.")
    except AttributeError:
        return JsonMessageResponseUnauthorized("You do not have access to this Web service")

    return JsonMessageResponseForbidden("You do not have access to this Web service")

@login_required
def explode(request):
    raise Exception("KA BLAM")


@login_required
@profile_required
def password(request):
    if request.method != "POST":
        return JsonMessageResponseNotAllowed(["POST"])

    profile = request.user.get_profile()
    (valid, errormsg) = profile.change_password(request)
    if not valid:
        return JsonMessageResponseServerError(errormsg)

    return JsonMessageResponse("Password changed successfully")


@login_required
def preview(request):
    # The standard response upon error.
    def unavailable(reason="No preview is available for the requested file."):
        # Cache some metadata about the preview so we can retrieve it later.
        key = preview_key(uri)
        memcache_client().set(key, json.dumps({
            "error": True,
            "size": size,
            "truncated": False,
            "type": content_type,
        }), time=settings.PREVIEW_METADATA_EXPIRY)

        return render_page("errors/preview-unavailable.html", request, reason=reason, response=HttpResponseServerError())

    try:
        uri = request.GET["uri"]
    except KeyError:
        # This is the one case where we won't return the generic preview
        # unavailable response, since the request URI itself is malformed.
        logger.error("Malformed request: 'uri' not found in GET variables")
        return render_page("errors/404.html", request, response=HttpResponseNotFound())

    logger.debug("Attempting to preview URI '%s'", uri)

    # Set initial values for the size and content_type variables so we can call
    # unavailable() immediately.
    size = 0
    content_type = "application/octet-stream"

    # Get the actual file size.
    ls_request = GetRequest("ws/fs/ls", { "uri": uri })
    http = memcache_http(request)
    resp, content = http.make_request(ls_request)

    if resp.status != 200:
        logger.warning("Attempted to preview inaccessible URI '%s'", uri)
        return unavailable("No preview is available as the requested file is inaccessible.")

    result = json.loads(content)

    if len(result) != 1 or len(result.values()[0]["files"]) != 1:
        logger.warning("Unexpected number of ls results for URI '%s'", uri)
        return unavailable()

    size = result.values()[0]["files"][0][1]

    # Now get the file contents.
    params = {
        "uri": uri,
        "bytes": min(size, settings.PREVIEW_SIZE_LIMIT),
    }

    get_request = GetRequest("ws/fs/get", params)
    resp, content = http.make_request(get_request)

    if resp.status != 200:
        logger.warning("Attempted to preview inaccessible URI '%s'", uri)
        return unavailable("No preview is available as the requested file is inaccessible.")

    # Check the content type.
    if ";" in resp["content-type"]:
        content_type, charset = resp["content-type"].split(";", 1)
    else:
        content_type = resp["content-type"]
        charset = None

    if content_type not in settings.PREVIEW_SETTINGS:
        logger.debug("Preview of URI '%s' unsuccessful due to unknown MIME type '%s'", uri, content_type)
        return unavailable("Files of this type cannot be previewed.")

    type_settings = settings.PREVIEW_SETTINGS[content_type]
    content_type = type_settings.get("override_mime_type", content_type)

    # If the file is beyond the size limit, we'll need to check whether to
    # truncate it or not.
    truncated = False
    if size > settings.PREVIEW_SIZE_LIMIT:
        if type_settings.get("truncate", False):
            logger.debug("URI '%s' is too large: size %d > limit %d; truncating", uri, size, settings.PREVIEW_SIZE_LIMIT)
            content = content[0:settings.PREVIEW_SIZE_LIMIT]
            truncated = True
        else:
            logger.debug("URI '%s' is too large: size %d > limit %d", uri, size, settings.PREVIEW_SIZE_LIMIT)
            return unavailable("This file is too large to be previewed.")

    # Cache some metadata about the preview so we can retrieve it later.
    key = preview_key(uri)
    memcache_client().set(key, json.dumps({
        "error": False,
        "size": size,
        "truncated": settings.PREVIEW_SIZE_LIMIT if truncated else False,
        "type": content_type,
    }), time=settings.PREVIEW_METADATA_EXPIRY)

    # Set up our response.
    if charset:
        content_type += ";" + charset

    response = HttpResponse(content_type=content_type)

    # This disables content type sniffing in IE, which could otherwise be used
    # to enable XSS attacks.
    response["X-Content-Type-Options"] = "nosniff"

    logger.debug("Preview of URI '%s' successful; sending response", uri)

    # The original plan was to verify the MIME type that we get back from
    # Admin, but honestly, it's pretty useless in many cases. Let's just do the
    # best we can with the extension.
    if type_settings.get("sanitise"):
        try:
            response.write(html.sanitise(content))
        except RuntimeError:
            return unavailable("This HTML file is too deeply nested to be previewed.")
        except UnicodeEncodeError:
            return unavailable("This HTML file includes malformed Unicode, and hence can't be previewed.")
    else:
        response.write(content)

    return response

@login_required
def preview_metadata(request):
    if request.method != "GET":
        return JsonMessageResponseNotAllowed(["GET"])

    try:
        uri = request.GET["uri"]
    except KeyError:
        return JsonMessageResponseBadRequest("No URI parameter given")

    key = preview_key(uri)
    metadata = memcache_client().get(key)

    if metadata:
        return HttpResponse(metadata, content_type="application/json; charset=UTF-8")

    return JsonMessageResponseNotFound("Metadata not in cache")


# Error page views.
def error_404(request):
    return render_page("errors/404.html", request, response=HttpResponseNotFound())

def error_500(request):
    return render_page("errors/500.html", request, response=HttpResponseServerError())

    
# Implementation methods

@profile_required
def upload_file(request, user):
    logger.debug('')

    host = urlparse(settings.YABIADMIN_SERVER).hostname
    port = urlparse(settings.YABIADMIN_SERVER).port
    upload_path = urlparse(settings.YABIADMIN_SERVER).path

    while len(upload_path) and upload_path[-1]=='/':
        upload_path = upload_path[:-1]
        
    # we parse the GET portion of the request to find the passed in URI before we access the request object more deeply and trigger the processing
    upload_uri = request.GET['uri']
    
    # examine cookie jar for our admin session cookie
    http = memcache_http(request)
    jar = http.cookie_jar
    cookie_string = jar.cookies_to_send_header(settings.YABIADMIN_SERVER)['Cookie']
    
    streamer = FileUploadStreamer(host=host, port=port or 80, selector=upload_path+"/ws/fs/put?uri=%s"%quote(upload_uri), cookies=[cookie_string], fields=[])
    request.upload_handlers = [ streamer ]
    
    # evaluating POST triggers the processing of the request body
    request.POST
    
    result=streamer.stream.getresponse()
    
    content=result.read()
    status=int(result.status)
    reason = result.reason
    
    #print "passing back",status,reason,"in json snippet"
    
    response = {
        "level":"success" if status==200 else "failure",
        "message":content
        }
    return HttpResponse(content=json.dumps(response))

@profile_required
def yabiadmin_login(request, username, password):
    # TODO get the url from somewhere
    login_request = PostRequest('ws/login', params= {
        'username': username, 'password': password})
    http = memcache_http(request)
    resp, contents = http.make_request(login_request)
    if resp.status != 200: 
        return False, "System Error:"+contents
    json_resp = json.loads(contents)
    http.finish_session()
    
    success = json_resp.get('success', False)
    message = json_resp.get('message', "System Error")
    
    return success, message




@login_required
def exception_view(request):
    logger.debug("test exception view")
    raise Exception("This is a test exception.")
