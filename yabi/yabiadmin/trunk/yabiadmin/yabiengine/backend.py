from django.conf import settings
import httplib
from urllib import urlencode
import logging
logger = logging.getLogger('yabiengine')


def ls(directory):
    logger.info("Listing: %s" % directory)
    data = {'dir':directory}
    data = urlencode(data)
    headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
    conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
    conn.request('POST', settings.YABIBACKEND_LIST, data, headers)
    r = conn.getresponse()

    return r.read()

    # do a try catch on status
