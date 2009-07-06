from django.conf import settings
import httplib
from urllib import urlencode
import logging
logger = logging.getLogger('yabiengine')
from yabiadmin.yabmin.models import Backend
from django.core.exceptions import ObjectDoesNotExist


def ls(uri):
    logger.info("Listing: %s" % uri)

    data = {'dir':translate_uri(uri)}
    data = urlencode(data)
    headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
    conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
    conn.request('POST', settings.YABIBACKEND_LIST, data, headers)
    r = conn.getresponse()

    return r.read()

    # do a try catch on status



def translate_uri(uri):

    from urlparse import urlparse, urlsplit
    scheme, rest = uri.split(":",1)
    u = urlparse(rest)

    try:
        backend = Backend.objects.get(scheme=scheme, hostname=u.hostname)
    except ObjectDoesNotExist, e:
        # deliberately not doing anything with this exception here
        # so it bubbles up to annoy us
        raise
    
    return "%s/%s%s" % (backend.name, u.username, u.path)

