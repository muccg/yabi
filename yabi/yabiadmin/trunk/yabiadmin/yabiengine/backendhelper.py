# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import simplejson as json
import httplib
import socket
import os
from os.path import splitext
from urllib import urlencode, quote
from yabiadmin.yabiengine.urihelper import uriparse, get_backend_userdir
from yabiadmin.yabmin.models import Backend, BackendCredential
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.servers.basehttp import FileWrapper



import logging
logger = logging.getLogger('yabiengine')


def get_backendcredential_for_uri(yabiusername, uri):
    """
    Looks up a backend credential based on the supplied uri, which should include a username.
    Returns bc, will log and reraise ObjectDoesNotExist and MultipleObjectsReturned exceptions if more than one credential
    """
    logger.debug('yabiusername: %s uri: %s'%(yabiusername,uri))

    # parse the URI into chunks
    schema, rest = uriparse(uri)

    logger.debug('yabiusername: %s schema: %s usernamea :%s hostnamea :%s patha :%s'%(yabiusername,schema,rest.username,rest.hostname,rest.path))
    
    path = rest.path

    # get our set of credential candidates
    bcs = BackendCredential.objects.filter(credential__user__name=yabiusername,
                                           backend__scheme=schema,
                                           credential__username=rest.username,
                                           backend__hostname=rest.hostname)
    
    logger.debug("potential credentials [%s]" % (",".join([str(x) for x in bcs])))
    
    # TODO: fix this exec/fs credential problem expressed here
    # if there is only one in bcs, then we will assume its for us. This enables a request for uri = "gridftp://user@host/" to match the credential for "gridftp://user@host/scratch/bi01/" if there is only one cred
    # this keeps globus working on the gridftp credential
    if len(bcs)==1:
        logger.debug("assuming credential: %s" % bcs[0])
        return bcs[0]
    
    # lets look at the paths for these to find candidates
    cred = None
    for bc in bcs:
        checkpath = os.path.join(bc.backend.path,bc.homedir)

        # allow path to make with and without trailing /
        alternate_path = path
        if alternate_path.endswith('/'):
            alternate_path = alternate_path.rstrip('/')
        else:
            alternate_path += '/'

        logger.debug("path: %s alternate: %s bc.homedir: %s bc.backend.path: %s checkpath: %s" % (path,alternate_path,bc.homedir,bc.backend.path,checkpath))
        
        if path.startswith(checkpath) or alternate_path.startswith(checkpath):
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
    
    logger.debug("using credential: %s" % cred)
    return cred

def POST(resource, datadict, extraheaders={}, server=None):
    """Do a x-www-form-urlencoded style POST. That is NOT a file upload style"""
    data = urlencode(datadict)
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    headers.update(extraheaders)
    server = server if server else settings.YABIBACKEND_SERVER
    conn = httplib.HTTPConnection(server)
    conn.request('POST', resource, data, headers)
    logger.debug("resource: %s headers: %s"%(resource,headers))
    return conn.getresponse()

def get_file_list(yabiusername, uri, recurse=True):
    """
    Return a list of file tuples
    """
    logger.debug('yabiusername: %s uri: %s'%(yabiusername,uri))

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_LIST, quote(uri))
        if recurse:
            resource += "&recurse"
        logger.debug('server: %s resource: %s' % (settings.YABIBACKEND_SERVER, resource))

        bc = get_backendcredential_for_uri(yabiusername, uri)
        data = dict([('username', bc.credential.username),
                    ('password', bc.credential.password),
                    ('cert', bc.credential.cert),
                    ('key', bc.credential.key)])
        
        r = POST(resource,data)
       
        # TODO Code path relies on not always getting a 200 from the backend, so we cant assert 200

        file_list = []
        if r.status == 200:

            results = json.loads(r.read())
            
            logger.debug("json: %s" % results)
            shortpath=reduce(lambda x,y: x if len(x)<len(y) else y,results.keys())
            spl = len(shortpath)
            
            for key in results.keys():
                for file in results[key]["files"]:
                    file_list.append([os.path.join(key[spl:],file[0])]+file[1:])

        logger.debug("returning: %s" % file_list)
        return file_list
 
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise



def get_first_matching_file(yabiusername, uri, extension_list):
    logger.debug('yabiusername: %s uri: %s'%(yabiusername,uri))

    file_list = get_file_list(yabiusername, uri, recurse=False)
    filename = None

    # TODO similar code to is_task_file_valid on EngineJob, can we combine?
    for f in file_list:
        if (splitext(f[0])[1].strip('.') in extension_list) or ('*' in extension_list):
            filename = f[0]
            break

    return filename
        
        
    

def get_listing(yabiusername, uri):
    """
    Return a listing from backend
    """
    logger.debug('yabiusername: %s uri: %s'%(yabiusername,uri))

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_LIST, quote(uri))
        logger.debug('server: %s resource: %s' % (settings.YABIBACKEND_SERVER, resource))

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

    assert(r.status == 200)
    return r.read()


def mkdir(yabiusername, uri):
    """
    Make a directory via the backend
    """
    logger.debug('yabiusername: %s uri: %s'%(yabiusername,uri))
    
    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_MKDIR, quote(uri))
        logger.debug('server: %s resource: %s' % (settings.YABIBACKEND_SERVER, resource))

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

    assert(r.status == 200)
    return r.read() 

def get_backend_list(yabiusername):
    """
    Returns a list of backends for user, returns in json as the plain list is passed to the
    twisted backend which returns json
    """
    logger.debug('yabiusername: %s'%(yabiusername))

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

def get_file(yabiusername, uri):
    """
    Return a file at given uri
    """
    logger.debug('yabiusername: %s uri: %s'%(yabiusername,uri))

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_GET, quote(uri))
        logger.debug('server: %s resource: %s' % (settings.YABIBACKEND_SERVER, resource))

        bc = get_backendcredential_for_uri(yabiusername, uri)
        data = dict([('username', bc.credential.username),
                    ('password', bc.credential.password),
                    ('cert', bc.credential.cert),
                    ('key', bc.credential.key)])
        r = POST(resource,data)
        
        assert(r.status == 200)
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
    logger.debug('yabiusername: %s uri: %s'%(yabiusername,uri))

    recurse = '&recurse' if uri[-1]=='/' else ''

    try:
        resource = "%s?uri=%s%s" % (settings.YABIBACKEND_RM, quote(uri),recurse)
        logger.debug('server: %s resource: %s' % (settings.YABIBACKEND_SERVER, resource))

        bc = get_backendcredential_for_uri(yabiusername, uri)
        data = dict([('username', bc.credential.username),
                    ('password', bc.credential.password),
                    ('cert', bc.credential.cert),
                    ('key', bc.credential.key)])
        r = POST(resource,data)
        data=r.read()

        assert(r.status == 200)
        return r.status, data
 
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise


def copy_file(yabiusername, src, dst):
    """Send a request to the backend to perform the specified file copy"""
    logger.debug('yabiusername: %s src: %s dst: %s'%(yabiusername,src,dst))
    
    recurse = '&recurse' if src[-1]=='/' else ''
    
    try:
        resource = "%s?src=%s&dst=%s%s" % (settings.YABIBACKEND_COPY, quote(src), quote(dst),recurse)
        logger.debug('server: %s resource: %s' % (settings.YABIBACKEND_SERVER, resource))

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
        data=r.read()
        assert(r.status == 200)
        return r.status, data
 
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise
    
def send_upload_hash(yabiusername,uri,uuid):
    """Send an upload has to the backend. Returns the url returned by the backend for uploading"""
    logger.debug('yabiusername: %s uri: %s uuid: %s'%(yabiusername,uri,uuid))
    
    try:
        resource = "%s?uri=%s&uuid=%s&yabiusername=%s"%(settings.YABIBACKEND_UPLOAD,uri,uuid,yabiusername)
        logger.debug('server: %s resource: %s'%(settings.YABIBACKEND_SERVER, resource))
        
        # get credentials for uri destination backend
        bc = get_backendcredential_for_uri(yabiusername, uri)
        
        # construct information to post to backend
        data = {    'username'  : bc.credential.username,
                    'password'  : bc.credential.password,
                    'cert'      : bc.credential.cert,
                    'key'       : bc.credential.key,
                    'uri'       : uri,
                    'uuid'      : uuid,
                    'yabiusername' : yabiusername       }
                    
        logger.debug( "POST"+resource )
        logger.debug( "DATA"+str(data) )
                    
        r = POST(resource, data)
        result = r.read()
        logger.debug("status:"+str(r.status))
        logger.debug("data:"+str(r.data))
        assert(r.status == 200)
    
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise
    
    decoded = json.loads(result)
    return decoded['upload_url']
    
    # now we return to the client our upload url for client to POST to
    upload_url = "http://%s/upload/%s"%(settings.YABIBACKEND_SERVER)
    return upload_url

