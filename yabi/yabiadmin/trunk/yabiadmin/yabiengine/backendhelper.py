from django.conf import settings
from django.utils import simplejson as json
import httplib
import socket
from urllib import urlencode
from yabiadmin.yabiengine.urihelper import uri_get_pseudopath, uriparse, get_backend_uri, get_backend_userdir
from yabiadmin.yabmin.models import Backend, BackendCredential
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist

import logging
import yabilogging
logger = logging.getLogger('yabiengine')


def get_file_list(uri):
    """
    Return a list of file tuples
    """
    logger.debug('')
    logger.info("Listing: %s" % uri)

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_LIST, uri)
        logger.debug('Resource: %s' % resource)
        conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)
        conn.request('GET', resource)
        r = conn.getresponse()
 
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise

    logger.info("Status of return from yabi backend is: %s" % r.status)

    file_list = []
    if r.status == 200:

        results = json.loads(r.read())
        for key in results.keys():
            for file in results[key]["files"]:
                file_list.append(file)

    return file_list


def get_listing(uri):
    """
    Return a listing from backend
    """
    logger.debug('')
    logger.info("Listing: %s" % uri)

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_LIST, uri)
        logger.debug('Resource: %s' % resource)
        conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)
        conn.request('GET', resource)
        r = conn.getresponse()

    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise

    logger.info("Status of return from yabi backend is: %s" % r.status)

    return r.read()



def get_backend_from_uri(uri):
    """
    Returns a Backend object given a uri
    """
    logger.debug('')
    scheme, parts = uriparse(uri)

    try:

        return Backend.objects.get(scheme=scheme, hostname=parts.hostname)

    except ObjectDoesNotExist, e:
        logger.critical("ObjectDoesNotExist for uri: %s" % uri)
        logger.critical("Scheme: %s" % scheme)
        logger.critical("Hostname: %s" % parts.hostname)
        raise



def get_backend_list(yabiusername):
    """
    Returns a list of backends for user, returns in json as the plain list is passed to the
    twisted backend which returns json
    """
    logger.debug('')

    try:

        results = { yabiusername: {'files':[], 'directories':[] }}


        for bc in BackendCredential.objects.filter(credential__user__name=yabiusername):
            uri = get_backend_userdir(bc, yabiusername)
            results[yabiusername]['directories'].append([uri, 0, ''])

        return json.dumps(results)

    except ObjectDoesNotExist, e:
        logger.critical("ObjectDoesNotExist for uri: %s" % uri)
        logger.critical("Scheme: %s" % scheme)
        logger.critical("Hostname: %s" % parts.hostname)
        raise


