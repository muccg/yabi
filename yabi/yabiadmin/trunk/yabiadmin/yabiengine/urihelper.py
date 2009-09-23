from django.conf import settings
import httplib
from urllib import urlencode
from django.core.exceptions import ObjectDoesNotExist

import logging
import yabilogging
logger = logging.getLogger('yabiengine')


def uri_get_pseudopath(uri):
    logger.debug('')
    
    from yabiadmin.yabmin.models import Backend
    from urlparse import urlparse, urlsplit
    scheme, rest = uri.split(":",1)
    u = urlparse(rest)

    try:
        backend = Backend.objects.get(scheme=scheme, hostname=u.hostname)
    except ObjectDoesNotExist, e:
        logger.critical("Backend does not exist: %s %s" % (uri, u))
        # deliberately not doing anything with this exception here
        # so it bubbles up to annoy us
        raise
    
    return "%s/%s%s" % (backend.name, u.username, u.path)


def uriparse(uri):
    logger.debug('')

    """
    This function returns a tuple containing the scheme and the ParseResult object.
    It is done this way as urlparse only accepts a specific list of url schemes
    and yabi:// is not one of them. The ParseResult object is read-only so
    we cannot inject the scheme back into it.
    """
    from urlparse import urlparse
    logger.debug(uri)

    try:
        scheme, rest = uri.split(":",1)
        return (scheme, urlparse(rest))
    except ValueError, e:
        logger.critical("%s - ValueError for uri: %s" % ("urihelper.uriparse", uri))
        logger.critical("%s - %s" % ("urihelper.uriparse", e.message))
        raise
    except AttributeError, e:
        logger.critical("%s - AttributeError for uri: %s" % ("urihelper.uriparse", uri))
        logger.critical("%s - %s" % ("urihelper.uriparse", e.message))
        raise

    
def get_backend_uri(backend):
    logger.debug('Backend: %s' % backend)

    from yabiadmin.yabmin.models import Backend
    from urlparse import urlunparse
    assert isinstance(backend, Backend)

    # check for the things vital to building a uri
    if not backend.hostname:
        raise Exception('No backend hostname for backend: %s' % backend)
    if not backend.scheme:
        raise Exception('No backend scheme for backend: %s' % backend)

    netloc = backend.hostname
    if backend.port:
        netloc += ':%d' % backend.port

    return urlunparse((backend.scheme, netloc, backend.path, '', '', ''))


def get_backend_userdir(backendcredential, yabiusername):
    """
    Supplies the front end with a list of backend uris including the user's home dir
    """
    logger.debug('Backendcredential: %s' % backendcredential)

    from yabiadmin.yabmin.models import BackendCredential
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

