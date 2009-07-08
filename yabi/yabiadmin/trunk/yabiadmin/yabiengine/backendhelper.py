from django.conf import settings
from django.utils import simplejson as json
import httplib
from urllib import urlencode
from yabiadmin.yabiengine.urihelper import uri_get_pseudopath
import logging
logger = logging.getLogger('yabiengine')

from django.core.exceptions import ObjectDoesNotExist


def get_file_list(uri):
    """Return a list of file tuples"""
    
    logger.info("Listing: %s" % uri)

    data = {'dir': uri_get_pseudopath(uri)}
    data = urlencode(data)
    headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
    conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
    conn.request('POST', settings.YABIBACKEND_LIST, data, headers)
    r = conn.getresponse()

    logger.info("Status of return from yabi backend is: %s" % r.status)

    file_list = []
    if r.status == 200:

        results = json.loads(r.read())
        for key in results.keys():
            for file in results[key]["files"]:
                file_list.append(file)

    return file_list
