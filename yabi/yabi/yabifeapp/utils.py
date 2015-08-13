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

import hashlib
import json
from django.http import HttpResponse, HttpResponseRedirect
from ccg_django_utils.http import HttpResponseUnauthorized
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
from django.contrib.auth import logout as django_logout
from ccg_django_utils import webhelpers
from django.template.loader import render_to_string
from yaphc import Http, GetRequest, PostRequest, UnauthorizedError
from yaphc.django_cache_persister import DjangoCacheCookiePersister
import logging
logger = logging.getLogger(__name__)


def yabi_client(request):
    persister = DjangoCacheCookiePersister(
        key='cookies-%s' % request.session.session_key,
        cache_time=settings.SESSION_COOKIE_AGE)
    yabi = settings.YABIADMIN_SERVER
    return Http(base_url=yabi, cache=False, cookie_persister=persister)


def make_http_request(request, original_request, ajax_call):
    try:
        with yabi_client(original_request) as http:
            try:
                resp, contents = http.make_request(request)
                logger.debug("response status is: %d" % (resp.status))
                our_resp = HttpResponse(contents, status=int(resp.status))
                copy_non_empty_headers(resp, our_resp, ('content-disposition', 'content-type'))
                return our_resp
            except UnauthorizedError:
                logger.error("Cannot connect successfully to yabi admin. Is yabife set to connect to a valid admin via https?")
                if ajax_call:
                    return HttpResponseUnauthorized()
                else:
                    return HttpResponseRedirect(settings.LOGIN_URL + "?error=Cannot+authenticate+with+yabi+admin.")
    except ObjectDoesNotExist:
        if ajax_call:
            return HttpResponseUnauthorized()
        else:
            return HttpResponseRedirect(settings.LOGIN_URL)


def make_request_object(url, request):
    if request.method == 'GET':
        return GetRequest(url, request.GET.dict())

    elif request.method == 'POST':
        files = [('file%d' % (i + 1), f.name, f.temporary_file_path()) for i, f in enumerate(request.FILES.values())]
        return PostRequest(url, request.POST.dict(), files=files)


def copy_non_empty_headers(src, to, header_names):
    for header_name in header_names:
        header_value = src.get(header_name)
        if header_value:
            to[header_name] = header_value


def mail_admins_no_profile(user):
    mail_admins("User Profile Error", render_to_string("email/noprofile.txt", {
        "user": user,
    }))


def preview_key(uri):
    # The naive approach here is to use the file name encoded in such a way
    # that memcache accepts it as a key, but that turns out to be problematic,
    # as it's not uncommon for file names within YABI to be greater than the
    # 250 character limit memcache imposes on key names. As a result, we'll
    # hash the file name and accept the (extremely slight) risk of collisions.
    uri = uri.encode("utf-8")
    file_hash = hashlib.sha512(uri).hexdigest()
    return str("-preview-%s" % file_hash)


def yabi_passchange(request, currentPassword, newPassword):
    enc_request = PostRequest("ws/account/passchange", params={"currentPassword": currentPassword, "newPassword": newPassword})
    http = yabi_client(request)
    resp, content = http.make_request(enc_request)
    assert resp['status'] == '200', (resp['status'], content)


def logout(request):
    yabi_logout(request)
    django_logout(request)
    return HttpResponseRedirect(webhelpers.url("/"))


def yabi_logout(request):
    # TODO get the url from somewhere
    logout_request = PostRequest('ws/logout')
    try:
        with yabi_client(request) as http:
            resp, contents = http.make_request(logout_request)
            if resp.status != 200:
                return False
            json_resp = json.loads(contents)
        return json_resp.get('success', False)
    except (ObjectDoesNotExist, AttributeError):
        pass


def using_dev_settings():

    using_dev_settings = False

    # these should be true in production
    for s in ['SSL_ENABLED', 'SESSION_COOKIE_SECURE', 'SESSION_COOKIE_HTTPONLY', ]:
        if getattr(settings, s) is False:
            using_dev_settings = True
            break

    # these should be false in production
    for s in ['DEBUG']:
        if getattr(settings, s) is True:
            using_dev_settings = True
            break

    # SECRET_KEY
    if settings.SECRET_KEY == 'set_this':
        using_dev_settings = True

    return using_dev_settings
