# -*- coding: utf-8 -*-
# Create your views here.
import httplib
from urllib import urlencode, unquote, quote
import base64
import copy
import hashlib
import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError, HttpResponseUnauthorized
from django.shortcuts import render_to_response, get_object_or_404, render_mako
from django.core.exceptions import ObjectDoesNotExist
from django.utils import webhelpers
from django.contrib.auth.decorators import login_required
from yabife.decorators import authentication_required
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django.contrib.auth.models import SiteProfileNotAvailable, User as DjangoUser
from django import forms
from django.core.servers.basehttp import FileWrapper
from django.template.loader import get_template
from django.utils import simplejson as json

from yaphc import Http, GetRequest, PostRequest, UnauthorizedError
from yaphc.memcache_persister import MemcacheCookiePersister

from yabife.yabifeapp.models import User

from ldap import LDAPError, MOD_REPLACE
from yabife.ldapclient import LDAPClient
from yabife.ldaputils import get_userdn_of
from yabife.responses import *
from yabife.yabifeapp.preview import html as sanitise_html

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

    template = get_template(template)
    response.write(template.render(**context))

    return response

@login_required
def files(request):
    return render_page("files.html", request)

@login_required
def design(request, id=None):
    return render_page("design.html", request, reuseId=id)
    
@login_required
def jobs(request):
    return render_page("jobs.html", request)

@login_required
def account(request):
    if request.user.get_profile().has_account_tab():
        return render_page("account.html", request)

    return render_page("errors/403.html", request, response=HttpResponseForbidden())

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

@authentication_required
def credentialproxy(request, url):
    if request.user.get_profile().credential_access:
        return adminproxy(request, url)

    return JsonMessageResponseForbidden("You do not have access to this Web service")

@login_required
def password(request):
    if request.method != "POST":
        return JsonMessageResponseNotAllowed(["POST"])

    profile = request.user.get_profile()
    if not profile.user_option_access:
        return JsonMessageResponseForbidden("You do not have access to this Web service")

    required = ("currentPassword", "newPassword", "confirmPassword")
    for key in required:
        if key not in request.POST:
            return JsonMessageResponseBadRequest("Expected key '%s' not found in request" % key)

    # Check the current password.
    if not authenticate(username=request.user.username, password=request.POST["currentPassword"]):
        return JsonMessageResponseForbidden("Current password is incorrect")

    # The new passwords should at least match and meet whatever rules we decide
    # to impose (currently a minimum six character length).
    if request.POST["newPassword"] != request.POST["confirmPassword"]:
        return JsonMessageResponseBadRequest("The new passwords must match")

    if len(request.POST["newPassword"]) < 6:
        return JsonMessageResponseBadRequest("The new password must be at least 6 characters in length")

    # OK, let's actually try to change the password.
    request.user.set_password(request.POST["newPassword"])
    
    # And, more importantly, in LDAP if we can.
    try:
        userdn = get_userdn_of(request.user.username)
        client = LDAPClient(settings.AUTH_LDAP_SERVER)
        client.bind_as(userdn, request.POST["currentPassword"])

        md5 = hashlib.md5(request.POST["newPassword"]).digest()
        modlist = (
            (MOD_REPLACE, "userPassword", "{MD5}%s" % (base64.encodestring(md5).strip(), )),
        )
        client.modify(userdn, modlist)

        client.unbind()
    except (AttributeError, LDAPError), e:
        # Send back something fairly generic.
        logger.debug("Error connecting to server: %s" % str(e))
        return JsonMessageResponseServerError("Error changing password")

    request.user.save()

    return JsonMessageResponse("Password changed successfully")

@login_required
def preview(request):
    # The standard response upon error.
    def unavailable():
        return render_page("errors/preview-unavailable.html", request, response=HttpResponseServerError())

    try:
        uri = request.GET["uri"]
    except KeyError:
        # This is the one case where we won't return the generic preview
        # unavailable response, since the request URI itself is malformed.
        logger.error("Malformed request: 'uri' not found in GET variables")
        return render_page("errors/404.html", request, response=HttpResponseNotFound())

    logger.debug("Attempting to preview URI '%s'", uri)

    # Get the actual file size.
    ls_request = GetRequest("ws/fs/ls", { "uri": uri })
    http = memcache_http(request.user)
    resp, content = http.make_request(ls_request)

    if resp.status != 200:
        logger.warning("Attempted to preview inaccessible URI '%s'", uri)
        return unavailable()

    result = json.loads(content)

    if len(result) != 1 or len(result.values()[0]["files"]) != 1:
        logger.warning("Unexpected number of ls results for URI '%s'", uri)
        return unavailable()

    size = result.values()[0]["files"][0][1]

    # Now get the file contents, assuming it's small enough or we want to
    # truncate.
    if size > settings.PREVIEW_SIZE_LIMIT:
        logger.debug("URI '%s' is too large: size %d > limit %d", uri, size, settings.PREVIEW_SIZE_LIMIT)
        return unavailable()

    params = {
        "uri": uri,
        "bytes": min(size, settings.PREVIEW_SIZE_LIMIT),
    }

    get_request = GetRequest("ws/fs/get", params)
    resp, content = http.make_request(get_request)

    if resp.status != 200:
        logger.warning("Attempted to preview inaccessible URI '%s'", uri)
        return unavailable()

    # Check the content type.
    if ";" in resp["content-type"]:
        content_type, charset = resp["content-type"].split(";", 1)
    else:
        content_type = resp["content-type"]
        charset = None

    if content_type not in settings.PREVIEW_SETTINGS:
        logger.debug("Preview of URI '%s' unsuccessful due to unknown MIME type '%s'", uri, content_type)
        return unavailable()

    type_settings = settings.PREVIEW_SETTINGS[content_type]
    content_type = type_settings.get("override_mime_type", content_type)

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
        response.write(sanitise_html(content))
    else:
        response.write(content)

    return response

    
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
    try:
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
    except ObjectDoesNotExist:
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
    try:
        with memcache_http(username) as http:
            resp, contents = http.make_request(logout_request)
            if resp.status != 200: 
                return False
            json_resp = json.loads(contents)
        return json_resp.get('success', False)
    except ObjectDoesNotExist:
        pass
