# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import simplejson as json
import httplib
import socket
import os
from urllib import urlencode, quote
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
    logger.debug('credential request for yabiusername: %s uri: %s'%(yabiusername,uri))

    # parse the URI into chunks
    schema, rest = uriparse(uri)

    logger.debug('uriparse returned... yabiusername: %s schema:%s username:%s hostname:%s path:%s'%(yabiusername,schema,rest.username,rest.hostname,rest.path))
    
    path = rest.path

    logger.debug('BackendCredential filter credential__user__name=%s, backend__scheme=%s, credential__username=%s, backend__hostname=%s'%(yabiusername,schema,rest.username,rest.hostname))

    # get our set of credential candidates
    bcs = BackendCredential.objects.filter(credential__user__name=yabiusername,
                                           backend__scheme=schema,
                                           credential__username=rest.username,
                                           backend__hostname=rest.hostname)
    
    logger.debug("bc search found... ->%s<-" % (",".join([str(x) for x in bcs])))
    
    # if there is only one in bcs, then we will assume its for us. This enables a request for uri = "gridftp://user@host/" to match the credential for "gridftp://user@host/scratch/bi01/" if there is only one cred
    # this keeps globus working on the gridftp credential
    if len(bcs)==1:
        return bcs[0]
    
    # lets look at the paths for these to find candidates
    cred = None
    for bc in bcs:
        checkpath = os.path.join(bc.backend.path,bc.homedir)
        logger.debug("path:%s bcpath:%s bc.be.path:%s checkpath:%s"%(path,bc.homedir,bc.backend.path,checkpath))
        
        if path.startswith(checkpath):
            # valid. If homedir path is longer than the present stored one, replace the stored one with this one to user
            if cred==None:
                logger.debug("setting cred to %s",str(bc))
                cred = bc
            elif len(checkpath) > len(os.path.join(cred.backend.path,cred.homedir)):
                logger.debug("resetting cred to %s",str(bc))
                cred = bc
            
    # cred is now either None if there was no valid credential, or it is the credential for this URI
    if not cred:
        raise ObjectDoesNotExist("Could not find backendcredential")
    
    logger.debug("returning bc... %s" % cred)
    return cred

def POST(resource, datadict, extraheaders={}, server=None):
    """Do a x-www-form-urlencoded style POST. That is NOT a file upload style"""
    data = urlencode(datadict)
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    headers.update(extraheaders)
    
    server = server if server else settings.YABIBACKEND_SERVER
    
    conn = httplib.HTTPConnection(server)
    conn.request('POST', resource, data, headers)
    return conn.getresponse()

def get_file_list(yabiusername, uri, recurse=True):
    """
    Return a list of file tuples
    """
    logger.debug('')
    logger.info("yabiusername: %s" % yabiusername)
    logger.info("Listing: %s" % uri)

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_LIST, quote(uri))
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
            
            logger.debug("SHORTPATH: %s" % shortpath)
            
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
        resource = "%s?uri=%s" % (settings.YABIBACKEND_LIST, quote(uri))

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
    data = r.read()
    if r.status != 200:
        logger.debug("Result from yabi backend is: %s" %data)

    return data


def mkdir(yabiusername, uri):
    """
    Make a directory via the backend
    """
    logger.debug('')
    logger.info("backendhelper::mkdir(%s %r)" % (yabiusername, uri))
    
    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_MKDIR, quote(uri))

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

def get_backend_list(yabiusername):
    """
    Returns a list of backends for user, returns in json as the plain list is passed to the
    twisted backend which returns json
    """
    logger.debug('')

    try:

        results = { yabiusername: {'files':[], 'directories':[] }}

        for bc in BackendCredential.objects.filter(credential__user__name=yabiusername, visible=True):
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
        resource = "%s?uri=%s" % (settings.YABIBACKEND_GET, quote(uri))
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

    recurse = '&recurse' if uri[-1]=='/' else ''

    try:
        resource = "%s?uri=%s%s" % (settings.YABIBACKEND_RM, quote(uri),recurse)
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
    
    recurse = '&recurse' if src[-1]=='/' else ''
    
    try:
        resource = "%s?src=%s&dst=%s%s" % (settings.YABIBACKEND_COPY, quote(src), quote(dst),recurse)
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


