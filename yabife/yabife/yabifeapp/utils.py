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

import memcache, hashlib, os

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from ccg.http import HttpResponseUnauthorized
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
from django.contrib.auth import login as django_login, logout as django_logout
from ccg.utils import webhelpers
from django.template.loader import render_to_string
from django.utils import simplejson as json

from yaphc import Http, GetRequest, PostRequest, UnauthorizedError
from yaphc.memcache_persister import MemcacheCookiePersister
from yaphc.cookies import FileCookiePersister

import logging
logger = logging.getLogger(__name__)

def memcache_client():
    return memcache.Client(settings.MEMCACHE_SERVERS)


def yabiadmin_client(request):
    user = request.user

    if settings.MEMCACHE_SERVERS:
        mp = MemcacheCookiePersister(settings.MEMCACHE_SERVERS,
                key='%s-cookies-%s' %(settings.MEMCACHE_KEYSPACE, request.session.session_key),
                cache_time=settings.SESSION_COOKIE_AGE)
    else:
        mp = FileCookiePersister(os.path.join(settings.FILE_COOKIE_DIR, settings.FILE_COOKIE_NAME))

    yabiadmin = settings.YABIADMIN_SERVER
    return Http(base_url=yabiadmin, cache=False, cookie_persister=mp)


def make_http_request(request, original_request, ajax_call):
    try:
        with yabiadmin_client(original_request) as http:
            try:
                resp, contents = http.make_request(request)
                logger.debug("response status is: %d"%(resp.status))
                our_resp = HttpResponse(contents, status=int(resp.status))
                copy_non_empty_headers(resp, our_resp, ('content-disposition', 'content-type'))
                return our_resp
            except UnauthorizedError:
                logger.error("Cannot connect successfully to yabi admin. Is yabife set to connect to a valid admin via https?")
                if ajax_call:
                    return HttpResponseUnauthorized() 
                else:
                    return HttpResponseRedirect(settings.LOGIN_URL+"?error=Cannot+authenticate+with+yabi+admin.")
    except ObjectDoesNotExist:
        if ajax_call:
            return HttpResponseUnauthorized() 
        else:
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
    file_hash = hashlib.sha512(uri).hexdigest()
    return str("%s-preview-%s" % (settings.MEMCACHE_KEYSPACE, file_hash))


def yabiadmin_passchange(request, currentPassword, newPassword):
    enc_request = PostRequest("ws/account/passchange", params={ "currentPassword": currentPassword, "newPassword": newPassword })
    http = yabiadmin_client(request)
    resp, content = http.make_request(enc_request)
    assert resp['status']=='200', (resp['status'], content)


def logout(request):
    yabiadmin_logout(request)
    django_logout(request)
    return HttpResponseRedirect(webhelpers.url("/"))


def yabiadmin_logout(request):
    # TODO get the url from somewhere
    logout_request = PostRequest('ws/logout')
    try:
        with yabiadmin_client(request) as http:
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
        if getattr(settings, s) == False:
            using_dev_settings = True
            break

    # these should be false in production
    for s in ['DEBUG']:
        if getattr(settings, s) == True:
            using_dev_settings = True
            break

    # SECRET_KEY
    if settings.SECRET_KEY == 'set_this':
        using_dev_settings = True

    # YABIADMIN_SERVER
    if not settings.YABIADMIN_SERVER.startswith('https://'):
        using_dev_settings = True

    return using_dev_settings
