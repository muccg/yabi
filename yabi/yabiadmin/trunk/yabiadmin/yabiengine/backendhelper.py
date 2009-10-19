from django.conf import settings
from django.utils import simplejson as json
import httplib
import socket
import os
from urllib import urlencode
from yabiadmin.yabiengine.urihelper import uri_get_pseudopath, uriparse, get_backend_userdir
from yabiadmin.yabmin.models import Backend, BackendCredential
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.core.servers.basehttp import FileWrapper



import logging
import yabilogging
logger = logging.getLogger('yabiengine')


def get_file_list(uri, recurse=True):
    """
    Return a list of file tuples
    """
    logger.debug('')
    logger.info("Listing: %s" % uri)

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_LIST, uri)
        if recurse:
            resource += "&recurse"
        logger.debug('Resource: %s' % resource)
        conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)
        conn.request('GET', resource)
        r = conn.getresponse()

        logger.info("Status of return from yabi backend is: %s" % r.status)
        
        file_list = []
        if r.status == 200:

            results = json.loads(r.read())
            
            print "FILELIST RESULTS:",results
            shortpath=reduce(lambda x,y: x if len(x)<len(y) else y,results.keys())
            spl = len(shortpath)
            
            for key in results.keys():
                for file in results[key]["files"]:
                    print "KEY",key,"FILE",file
                    file_list.append([os.path.join(key[spl:],file[0])]+file[1:])

        print "RETURNING:",file_list
        return file_list
 
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise


def get_listing(uri):
    """
    Return a listing from backend
    """
    logger.debug('')
    logger.info("Listing: %s" % uri)

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_LIST, uri)
        logger.debug('Resource: %s' % resource)
        print 'Resource: %s' % resource
        conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
        print 'Server: %s' % settings.YABIBACKEND_SERVER
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)
        conn.request('GET', resource)
        r = conn.getresponse()
        print 'response',r

    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise

    logger.info("Status of return from yabi backend is: %s" % r.status)

    print "reading"
    return r.read()


def mkdir(uri):
    """
    Make a directory via the backend
    """
    logger.debug('')
    logger.info("backendhelper::mkdir(%r)"%uri)
    
    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_MKDIR, uri)
        logger.debug('Resource: %s' % resource)
        print 'Resource: %s' % resource
        conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
        print 'Server: %s' % settings.YABIBACKEND_SERVER
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)
        conn.request('GET', resource)
        r = conn.getresponse()
        print 'response',r

    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise

    logger.info("Status of return from yabi backend is: %s" % r.status)

    print "reading"
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
            results[yabiusername]['directories'].append([bc.homedir_uri, 0, ''])

        return json.dumps(results)

    except ObjectDoesNotExist, e:
        logger.critical("ObjectDoesNotExist for uri: %s" % uri)
        logger.critical("Scheme: %s" % scheme)
        logger.critical("Hostname: %s" % parts.hostname)
        raise



def put_file(uri, fh):
    """
    Upload a file to the backend
    """
    logger.debug('')


## curl -F file1=@index.html -F file2=@fish.csv
## faramir:8100/fs/put?uri=gridftp://cwellington@xe-ng2.ivec.org/scratch/bi01/cwellington/

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_PUT, uri)
        logger.debug('Resource: %s' % resource)
        conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)
        conn.request('GET', resource, fh)
        r = conn.getresponse()
        logger.info("Status of return from yabi backend is: %s" % r.status)
 
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise


def get_file(uri):
    """
    Return a file at given uri
    """
    logger.debug('')
    logger.info("Getting: %s" % uri)

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_GET, uri)
        logger.debug('Resource: %s' % resource)
        conn = httplib.HTTPConnection(settings.YABIBACKEND_SERVER)
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)
        conn.request('GET', resource)
        r = conn.getresponse()

        logger.info("Status of return from yabi backend is: %s" % r.status)

        return FileWrapper(r, blksize=1024**2)
 
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise





## this is not used, was from here
##    http://metalinguist.wordpress.com/2008/02/12/django-file-and-stream-serving-performance-gotcha/
## but there is a build in FileWrapper object here django.core.servers.basehttp import FileWrapper
## that we use instead
## remove eventually, left here for reference for now

## class FileIterWrapper(object):
##     def __init__(self, flo, chunk_size = 1024**2):
##         self.flo = flo
##         self.chunk_size = chunk_size

##     def next(self):
##         data = self.flo.read(self.chunk_size)
##         if data:
##             return data
##         else:
##             raise StopIteration

##     def __iter__(self):
##         return self


