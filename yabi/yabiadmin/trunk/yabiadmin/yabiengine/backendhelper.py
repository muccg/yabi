from django.conf import settings
from django.utils import simplejson as json
import httplib
import socket
import os
from urllib import urlencode
from yabiadmin.yabiengine.urihelper import uriparse, get_backend_userdir
from yabiadmin.yabmin.models import Backend, BackendCredential
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.servers.basehttp import FileWrapper



from django.contrib import logging
logger = logging.getLogger('yabiengine')


def get_backendcredential_for_uri(yabiusername, uri):
    """
    Looks up a backend credential based on the supplied uri, which should include a username.
    Returns bc, will log and reraise ObjectDoesNotExist and MultipleObjectsReturned exceptions if more than one credential
    """
    scheme, uriparts = uriparse(uri)
    try:
        bc = BackendCredential.objects.get(credential__user__name=yabiusername,
                                           backend__hostname=uriparts.hostname,
                                           backend__scheme=scheme,
                                           credential__username=uriparts.username)
        return bc
    except (ObjectDoesNotExist,MultipleObjectsReturned), e:
        logger.critical(e)
        raise    


def POST(resource, datadict, extraheaders={}, server=None):
    """Do a x-www-form-urlencoded style POST. That is NOT a file upload style"""
    data = urlencode(datadict)
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    headers.update(extraheaders)
    
    server = server if server else settings.YABIBACKEND_SERVER
    
    conn = httplib.HTTPConnection(server)
    conn.request('POST', resource, data, headers)
    return conn.getresponse()

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
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)


        bc = get_backendcredential_for_uri(yabiusername, uri)
        data = dict([('username', bc.credential.username),
                    ('password', bc.credential.password),
                    ('cert', bc.credential.cert),
                    ('key', bc.credential.key)])
        
        r = POST(resource,data)

        logger.info("Status of return from yabi backend is: %s" % r.status)
        
        file_list = []
        if r.status == 200:

            results = json.loads(r.read())
            
            logger.debug("FILELIST RESULTS: %s" % results)
            shortpath=reduce(lambda x,y: x if len(x)<len(y) else y,results.keys())
            spl = len(shortpath)
            
            for key in results.keys():
                for file in results[key]["files"]:
                    logger.debug("KEY: %s FILE: %s" %(key,file))
                    file_list.append([os.path.join(key[spl:],file[0])]+file[1:])

        logger.debug("RETURNING: %s" %file_list)
        return file_list
 
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise


def get_listing(yabiusername, uri):
    """
    Return a listing from backend
    """
    logger.debug('')
    logger.info("Listing: %s" % uri)

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_LIST, uri)

        logger.debug('Resource: %s' % resource)
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)

        bc = get_backendcredential_for_uri(yabiusername, uri)
        data = dict([('username', bc.credential.username),
                    ('password', bc.credential.password),
                    ('cert', bc.credential.cert),
                    ('key', bc.credential.key)])
        r = POST(resource,data)

    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise

    logger.info("Status of return from yabi backend is: %s" % r.status)

    logger.debug("reading")
    return r.read()


def mkdir(yabiusername, uri):
    """
    Make a directory via the backend
    """
    logger.debug('')
    logger.info("backendhelper::mkdir(%s %r)" % (yabiusername, uri))
    
    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_MKDIR, uri)

        logger.debug('Resource: %s' % resource)
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)

        bc = get_backendcredential_for_uri(yabiusername, uri)
        data = dict([('username', bc.credential.username),
                    ('password', bc.credential.password),
                    ('cert', bc.credential.cert),
                    ('key', bc.credential.key)])
        r = POST(resource,data)

    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise

    logger.info("Status of return from yabi backend is: %s" % r.status)

    logger.debug("reading")
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

    assert False, "Is this deprecated?"


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


def get_file(yabiusername, uri):
    """
    Return a file at given uri
    """
    logger.debug('')
    logger.info("Getting: %s" % uri)

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_GET, uri)
        logger.debug('Resource: %s' % resource)
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)

        bc = get_backendcredential_for_uri(yabiusername, uri)
        data = dict([('username', bc.credential.username),
                    ('password', bc.credential.password),
                    ('cert', bc.credential.cert),
                    ('key', bc.credential.key)])
        r = POST(resource,data)
        
        logger.info("Status of return from yabi backend is: %s" % r.status)

        return FileWrapper(r, blksize=1024**2)
 
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise

def rm_file(yabiusername, uri):
    """
    Return a file at given uri
    """
    logger.debug('')
    logger.info("Removing: %s" % uri)

    try:
        resource = "%s?uri=%s&recurse" % (settings.YABIBACKEND_RM, uri)
        logger.debug('Resource: %s' % resource)
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)

        bc = get_backendcredential_for_uri(yabiusername, uri)
        data = dict([('username', bc.credential.username),
                    ('password', bc.credential.password),
                    ('cert', bc.credential.cert),
                    ('key', bc.credential.key)])
        r = POST(resource,data)
        
        logger.info("Status of return from yabi backend is: %s" % r.status)
        data=r.read()
        logger.debug("contents of return from yabi backend is: %s" % data)

        return r.status, data
 
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise


def copy_file(yabiusername, src, dst):
    """Send a request to the backend to perform the specified file copy"""
    logger.debug('')
    logger.info('Copying: %s -> %s' % (src,dst) )
    
    #if dst[-1]!="/":
        #dst+="/"
    
    try:
        resource = "%s?src=%s&dst=%s&recurse" % (settings.YABIBACKEND_COPY, src, dst)
        logger.debug('Resource: %s' % resource)
        logger.debug('Server: %s' % settings.YABIBACKEND_SERVER)

        # get credentials for src and destination backend
        src_bc = get_backendcredential_for_uri(yabiusername, src)
        dst_bc = get_backendcredential_for_uri(yabiusername, dst)
        data = dict([('src_username', src_bc.credential.username),
                    ('src_password', src_bc.credential.password),
                    ('src_cert', src_bc.credential.cert),
                    ('src_key', src_bc.credential.key),
                    ('dst_username', dst_bc.credential.username),
                    ('dst_password', dst_bc.credential.password),
                    ('dst_cert', dst_bc.credential.cert),
                    ('dst_key', dst_bc.credential.key)])
        r = POST(resource,data)
        
        logger.info("Status of return from yabi backend is: %s" % r.status)
        data=r.read()
        logger.debug("contents of return from yabi backend is: %s" % data)

        return r.status, data
 
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


