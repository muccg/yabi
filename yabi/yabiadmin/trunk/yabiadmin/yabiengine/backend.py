from django.conf import settings
import httplib
from urllib import urlencode
from yabiadmin.yabiengine.urihelper import uri2pseudopath
import logging
logger = logging.getLogger('yabiengine')

from django.core.exceptions import ObjectDoesNotExist


def ls(uri):
    logger.info("Listing: %s" % uri)

    data = {'dir': uri2pseudopath(uri)}
    data = urlencode(data)
    headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
    conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
    conn.request('POST', settings.YABIBACKEND_LIST, data, headers)
    r = conn.getresponse()

    logger.info("Status of return from yabi backend is: %s" % r.status)
    return r.read()



    # do a try catch on status
