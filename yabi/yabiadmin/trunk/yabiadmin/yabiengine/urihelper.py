from django.conf import settings
import httplib
from urllib import urlencode
from urlparse import urlparse

from django.core.exceptions import ObjectDoesNotExist

import logging
logger = logging.getLogger('yabiengine')

import re
re_url_schema = re.compile(r'\w+')


def uriparse(uri):
    """
    This function returns a tuple containing the scheme and the ParseResult object.
    It is done this way as urlparse only accepts a specific list of url schemes
    and yabi:// is not one of them. The ParseResult object is read-only so
    we cannot inject the scheme back into it.
    A copy of this function is in yabi-sh.
    """
    logger.debug(uri)

    try:
        scheme, rest = uri.split(":",1)
        assert re_url_schema.match(scheme)        
        return (scheme, urlparse(rest))
    except ValueError, e:
        logger.critical("%s - ValueError for uri: %s" % ("urihelper.uriparse", uri))
        logger.critical("%s - %s" % ("urihelper.uriparse", e.message))
        raise
    except AttributeError, e:
        logger.critical("%s - AttributeError for uri: %s" % ("urihelper.uriparse", uri))
        logger.critical("%s - %s" % ("urihelper.uriparse", e.message))
        raise


def url_join(*args):
    '''This is used to join subpaths to already constructed urls'''
    return reduce(lambda a,b: a+b if a.endswith('/') else a+'/'+b, args)

    
def get_backend_userdir(backendcredential, yabiusername):
    """
    Supplies the front end with a list of backend uris including the user's home dir
    """
    logger.debug('Backendcredential: %s' % backendcredential)

    from yabiadmin.yabi.models import BackendCredential
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

