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

import httplib
from urllib import urlencode
import copy
import os
from django.conf.urls import *
from django.conf import settings
from django.http import HttpResponse
import logging
logger = logging.getLogger(__name__)


# proxy view to pass through all requests set up in urls.py
def proxy(request, url, server, base):
    logger.debug(url)
    logger.debug(server)
    logger.debug(base)

    # TODO CODEREVIEW
    # Is is possible to post to a page and still send get params,
    # are they dropped by this proxy. Would it be possible to override yabiusername by
    # crafting a post and sending yabiusername as a get param as well

    if request.method == "GET":
        # resource = "%s?%s" % (os.path.join(base, url), request.META['QUERY_STRING']+"&yabiusername=%s"%quote(request.user.username) )
        resource = "%s?%s" % (os.path.join(base, url), request.META['QUERY_STRING'])
        logger.debug('Proxying get: %s%s' % (server, resource))
        conn = httplib.HTTPConnection(server)
        conn.request(request.method, resource)
        r = conn.getresponse()

    elif request.method == "POST":
        resource = os.path.join(base, url)
        post_params = copy.copy(request.POST)
        # post_params['yabiusername'] = request.user.username
        logger.debug('Proxying post: %s%s' % (server, resource))
        data = urlencode(post_params)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
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


def status_page(request):
    """Availability page to be called to see if yabi is running. Should return HttpResponse with status 200"""
    logger.info('')

    # write a file
    with open(os.path.join(settings.WRITABLE_DIRECTORY, 'status_page_testfile.txt'), 'w') as f:
        f.write("testing file write")

    # read it again
    with open(os.path.join(settings.WRITABLE_DIRECTORY, 'status_page_testfile.txt'), 'r') as f:
        contents = f.read()
        assert 'testing file write' in contents

    # delete the file
    os.unlink(os.path.join(settings.WRITABLE_DIRECTORY, 'status_page_testfile.txt'))

    return HttpResponse('Status OK')
