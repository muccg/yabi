# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
from django.conf.urls import *
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django import forms
from django.core.cache import cache
from django.template import RequestContext
from ccg_django_utils import webhelpers
from yabi.yabi.models import Credential, ModelBackendUserProfile, LDAPBackendUserProfile
from yabi.responses import *
from yabi.preview import html
from yabi.crypto_utils import DecryptException
from yabi.yabi.ws_frontend_views import ls, get
from yabi.yabifeapp.utils import preview_key, logout, using_dev_settings  # NOQA

import logging
logger = logging.getLogger(__name__)


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
    context = RequestContext(request, {
        "h": webhelpers,
        "settings": settings,
        "debug": debug,
        "base_site_url": webhelpers.url("").rstrip("/")
    })
    context.update(kwargs)
    return render_to_response(template, context)


@login_required
def files(request):
    return render_page("fe/files.html", request)


@login_required
def design(request, id=None):
    return render_page("fe/design.html", request, reuseId=id)


@login_required
def jobs(request):
    return render_page("fe/jobs.html", request)


@login_required
@user_passes_test(lambda user: user.is_staff)
def admin(request):
    return render_page("fe/admin.html", request)


@login_required
def account(request):
    profile = request.user.user
    if not profile.has_account_tab():
        return render_page("fe/errors/403.html", request, response=HttpResponseForbidden())

    username = request.user.username
    return render_page("fe/account.html", request, profile=profile, username=username)


def login(request):

    # show a warning if using dev settings
    show_dev_warning = using_dev_settings()

    def render_form(form, error='Invalid login credentials'):
        return render_to_response('fe/login.html', RequestContext(request, {
            'h': webhelpers,
            'base_site_url': webhelpers.url("").rstrip("/"),
            'form': form,
            'error': error,
            'show_dev_warning': show_dev_warning}))

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

                    # for every credential for this user, call the login hook
                    # currently creds will raise an exception if they can't be decrypted
                    # this is logged but user can still log in as they may have other creds
                    # that are still usable
                    creds = Credential.objects.filter(user__name=username)
                    for cred in creds:
                        try:
                            cred.on_login(username, password)
                        except DecryptException:
                            logger.error("Unable to decrypt credential `%s'" % cred.description)
                    next_page = request.GET.get('next', webhelpers.url("/"))
                    return HttpResponseRedirect(next_page)

            else:
                form = LoginForm()
                return render_form(form)

        else:
            return render_form(form)

    else:
        form = LoginForm()
        error = request.GET['error'] if 'error' in request.GET else ''
        return render_form(form, error)


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

            # for every credential for this user, call the login hook
            # currently creds will raise an exception if they can't be decrypted
            # this is logged but user can still log in as they may have other creds
            # that are still usable
            creds = Credential.objects.filter(user__name=username)
            for cred in creds:
                try:
                    cred.on_login(username, password)
                except DecryptException:
                    logger.error('Unable to decrypt credential %s' % cred.description)

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
    django_logout(request)
    response = {
        "success": True,
    }
    return HttpResponse(content=json.dumps(response))


@login_required
def password(request):
    if request.method != "POST":
        return JsonMessageResponseNotAllowed(["POST"])

    profile_class = ModelBackendUserProfile
    if settings.AUTH_TYPE == 'ldap':
        profile_class = LDAPBackendUserProfile

    profile = profile_class.objects.get(user=request.user)
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
        cache.set(key, json.dumps({
            "error": True,
            "size": size,
            "truncated": False,
            "type": content_type,
        }), settings.PREVIEW_METADATA_EXPIRY)

        return render_page("fe/errors/preview-unavailable.html", request, reason=reason, response=HttpResponseServerError())

    try:
        uri = request.GET["uri"]
    except KeyError:
        # This is the one case where we won't return the generic preview
        # unavailable response, since the request URI itself is malformed.
        logger.error("Malformed request: 'uri' not found in GET variables")
        return render_page("fe/errors/404.html", request, response=HttpResponseNotFound())

    logger.debug("Attempting to preview URI '%s'", uri)

    # Set initial values for the size and content_type variables so we can call
    # unavailable() immediately.
    size = 0
    content_type = "application/octet-stream"

    # Get the actual file size.
    resp = ls(request)
    if resp.status_code != 200:
        logger.warning("Attempted to preview inaccessible URI '%s'", uri)
        return unavailable("No preview is available as the requested file is inaccessible.")

    result = json.loads(resp.content)

    if len(result) != 1 or len(result.values()[0]["files"]) != 1:
        logger.warning("Unexpected number of ls results for URI '%s'", uri)
        return unavailable()

    size = result.values()[0]["files"][0][1]
    resp = get(request)

    if resp.status_code != 200:
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

    # Now work with the resulting file.
    # If the file is beyond the size limit, we'll need to check whether to
    # truncate it or not.
    truncated = False
    contents = []
    size = 0
    try:
        for chunk in resp.streaming_content:
            contents.append(chunk)
            size += len(chunk)
            if size > settings.PREVIEW_SIZE_LIMIT:
                if type_settings.get("truncate", False):
                    logger.debug("URI '%s' is too large: size %d > limit %d; truncating", uri, size, settings.PREVIEW_SIZE_LIMIT)
                    contents[-1] = contents[-1][:settings.PREVIEW_SIZE_LIMIT - size]
                    truncated = True
                    break
                else:
                    logger.debug("URI '%s' is too large: size %d > limit %d", uri, size, settings.PREVIEW_SIZE_LIMIT)
                    return unavailable("This file is too large to be previewed.")
        content = "".join(contents)
    except Exception:
        logger.exception("Problem when streaming response")
        return unavailable("The file could not be accessed.")

    # Cache some metadata about the preview so we can retrieve it later.
    key = preview_key(uri)
    cache.set(key, json.dumps({
        "error": False,
        "size": size,
        "truncated": settings.PREVIEW_SIZE_LIMIT if truncated else False,
        "type": content_type,
    }), settings.PREVIEW_METADATA_EXPIRY)

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
    metadata = cache.get(key)

    if metadata:
        return HttpResponse(metadata, content_type="application/json; charset=UTF-8")

    return JsonMessageResponseNotFound("Metadata not in cache")


# Error page views.
def error_404(request):
    return render_page("fe/errors/404.html", request, response=HttpResponseNotFound())


def error_500(request):
    return render_page("fe/errors/500.html", request, response=HttpResponseServerError())


@login_required
def exception_view(request):
    logger.debug("test exception view")
    raise Exception("This is a test exception.")


def handler404(request):
    return render_to_response('404.html', {'h': webhelpers})


def handler500(request):
    return render_to_response('500.html', {'h': webhelpers})
