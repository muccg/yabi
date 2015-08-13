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

from urlparse import urlparse
from functools import reduce
import re
import logging

logger = logging.getLogger(__name__)

re_url_schema = re.compile(r'\w+')


def uriparse(uri):
    """
    This function returns a tuple containing the scheme and the ParseResult object.
    It is done this way as urlparse only accepts a specific list of url schemes
    and yabi:// is not one of them. The ParseResult object is read-only so
    we cannot inject the scheme back into it.
    A copy of this function is in yabi-sh.
    """
    try:
        scheme, rest = uri.split(":", 1)
        assert re_url_schema.match(scheme)
        return (scheme, urlparse(rest))
    except ValueError as e:
        logger.critical("%s - ValueError for uri: %s" % ("urihelper.uriparse", uri))
        logger.critical("%s - %s" % ("urihelper.uriparse", e.message))
        raise
    except AttributeError as e:
        logger.critical("%s - AttributeError for uri: %s" % ("urihelper.uriparse", uri))
        logger.critical("%s - %s" % ("urihelper.uriparse", e.message))
        raise


def uriunparse(scheme, hostname, username, path='/', port=None):
    if port:
        uri = "%s://%s@%s:%s%s" % (scheme, username, hostname, port, path)
    else:
        uri = "%s://%s@%s%s" % (scheme, username, hostname, path)
    return uri


def url_join(*args):
    '''This is used to join subpaths to already constructed urls'''
    return reduce(lambda a, b: a + b if a.endswith('/') else a + '/' + b, args)


def get_backend_userdir(backendcredential, yabiusername):
    """
    Supplies the front end with a list of backend uris including the user's home dir
    """
    logger.debug('Backendcredential: %s' % backendcredential)

    from yabi.yabi.models import BackendCredential
    from urlparse import urlunparse
    assert isinstance(backendcredential, BackendCredential)

    # check for the things vital to building a uri
    if not backendcredential.backend.hostname:
        raise Exception('No backend hostname for backend: %s' % backendcredential.backend)
    if not backendcredential.backend.scheme:
        raise Exception('No backend scheme for backend: %s' % backendcredential.backend)

    netloc = "%s@%s" % (backendcredential.credential.username, backendcredential.backend.hostname)
    if backendcredential.backend.port:
        netloc += ':%d' % backendcredential.backend.port

    path = backendcredential.backend.path + backendcredential.homedir

    return urlunparse((backendcredential.backend.scheme, netloc, path, '', '', ''))


def is_same_location(uri, other_uri):
    uri_scheme, uri_rest = uriparse(uri)
    other_scheme, other_rest = uriparse(other_uri)
    return (uri_scheme == other_scheme and uri_rest.hostname == other_rest.hostname and uri_rest.port == other_rest.port)
