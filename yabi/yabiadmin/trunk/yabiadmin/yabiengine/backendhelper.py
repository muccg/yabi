from django.conf import settings
from django.utils import simplejson as json
import httplib
import socket
from urllib import urlencode
from yabiadmin.yabiengine.urihelper import uri_get_pseudopath, uriparse
from yabiadmin.yabmin.models import Backend
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
        data = {'dir': uri_get_pseudopath(uri)}
        data = urlencode(data)
        headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
        conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
        conn.request('POST', settings.YABIBACKEND_LIST, data, headers)
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



