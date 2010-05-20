# -*- coding: utf-8 -*-
import mimetypes
from urllib import quote

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from yabiadmin.yabmin.models import User, ToolGrouping, ToolGroup, Tool, ToolParameter, Credential, Backend, ToolSet, BackendCredential
from django.utils import webhelpers
from django.utils import simplejson as json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.conf import settings

from yabiadmin.yabiengine.storehelper import StoreHelper
from yabiadmin.yabiengine.tasks import build
from yabiadmin.yabiengine.enginemodels import EngineWorkflow
from yabiadmin.yabiengine.backendhelper import get_listing, get_backend_list, get_file, get_backendcredential_for_uri, copy_file, rm_file, send_upload_hash
from yabiadmin.security import validate_user, validate_uri
from yabiadmin.utils import json_error
from yabmin.file_upload import *

import uuid

import logging
logger = logging.getLogger('yabiadmin')

#
# Memcache stuff for this set of webservices
# lets help make the frontend more snappy
#
from django.contrib.memcache import KeyspacedMemcacheClient
mc = KeyspacedMemcacheClient()

def memcache(basekey,kwargkeylist,timout=120):
    def memcache_decorator(func):
        def memcache_decorated_func(request, *args, **kwargs):
            keyname = "-".join([basekey]+[str(kwargs[X]) for X in kwargkeylist])
            cached_result = mc.get(keyname)
            if cached_result:
                logger.debug("returning cached result for %s"%keyname)
                return HttpResponse(cached_result)
            
            # not cached. get real result.
            try:
                result = func(request, *args, **kwargs)
                mc.set(keyname,result,timeout)
                return HttpResponse(result)
            except ObjectDoesNotExist:
                return HttpResponseNotFound(json_error("Object not found"))
        return memcache_decorated_func
    return memcache_decorator
            

## TODO do we want to limit tools to those the user can access?
## will need to change call from front end to include username
## then uncomment decorator

#@validate_user
@memcache("tool",["toolname"],300)
def tool(request, *args, **kwargs):
    toolname = kwargs['toolname']
    logger.debug(toolname)

    return Tool.objects.get(name=toolname).json()


@validate_user
@memcache("menu",["username"])
def menu(request, *args, **kwargs):
    username = kwargs["username"]
    logger.debug(username)
    
    toolsets = ToolSet.objects.filter(users__name=username)
    output = {"toolsets":[]}

    # add each toolset
    for toolset in toolsets:

        ts = {}
        output["toolsets"].append(ts)
        ts["name"] = toolset.name
        ts["toolgroups"] = []


        # make up a dict of toolgroups
        toolgroups = {}

        for toolgroup in ToolGrouping.objects.filter(tool_set=toolset):
            if not toolgroup.tool_group.name in toolgroups:
                tg = {}
                toolgroups[toolgroup.tool_group.name] = tg
            else:
                tg = toolgroups[toolgroup.tool_group.name]

            if not "name" in tg:
                tg["name"] = toolgroup.tool_group.name
            if not "tools" in tg:
                tg["tools"] = []

            tool = {}
            tool["name"] = toolgroup.tool.name
            tool["displayName"] = toolgroup.tool.display_name
            tool["description"] = toolgroup.tool.description                
            tg["tools"].append(tool)
            tool["outputExtensions"] = toolgroup.tool.output_filetype_extensions()
            tool["inputExtensions"] = toolgroup.tool.input_filetype_extensions()


        # now add the toolgroups to toolsets
        for key, value in toolgroups.iteritems():
            ts["toolgroups"].append(value)


    return json.dumps({"menu":output})
    
@validate_uri
def ls(request):
    """
    This function will return a list of backends the user has access to IF the uri is empty. If the uri
    is not empty then it will pass on the call to the backend to get a listing of that uri
    """
    try:
        logger.debug("yabiusername: %s uri: %s" %(request.GET['yabiusername'], request.GET['uri']))
        if request.GET['uri']:
            filelisting = get_listing(request.GET['yabiusername'], request.GET['uri'])
        else:
            filelisting = get_backend_list(request.GET['yabiusername'])

        return HttpResponse(filelisting)
    except Exception, e:
        return HttpResponseNotFound(json_error(e))


@validate_uri
def copy(request):
    """
    This function will return a list of backends the user has access to IF the uri is empty. If the uri
    is not empty then it will pass on the call to the backend to get a listing of that uri
    """
    try:
        logger.debug("yabiusername: %s src: %s -> dst: %s" %(request.GET['yabiusername'], request.GET['src'],request.GET['dst']))
        status, data = copy_file(request.GET['yabiusername'],request.GET['src'],request.GET['dst'])

        return HttpResponse(content=data, status=status)
    except Exception, e:
        return HttpResponseNotFound(json_error(e))

@validate_uri
def rm(request):
    """
    This function will return a list of backends the user has access to IF the uri is empty. If the uri
    is not empty then it will pass on the call to the backend to get a listing of that uri
    """
    try:
        logger.debug("yabiusername: %s uri: %s" %(request.GET['yabiusername'], request.GET['uri']))
        status, data = rm_file(request.GET['yabiusername'],request.GET['uri'])

        return HttpResponse(content=data, status=status)
    except Exception, e:
        return HttpResponseNotFound(json_error(e))


@validate_uri
def get(request):
    """
    Returns the requested uri. get_file returns an httplib response wrapped in a FileIterWrapper. This can then be read
    by HttpResponse
    """
    try:
        logger.debug("yabiusername: %s uri: %s" %(request.GET['yabiusername'], request.GET['uri']))
        uri = request.GET['uri']
        yabiusername = request.GET['yabiusername']
        
        try:
            filename = uri.rsplit('/', 1)[1]
        except IndexError, e:
            logger.critical('Unable to get filename from uri: %s' % uri)
            filename = 'default.txt'

        response = HttpResponse(get_file(yabiusername, uri))

        mimetypes.init([os.path.normpath(os.path.expanduser('~/.yabi/mime.types')), os.path.normpath('/etc/yabi/mime.types')])
        type, encoding = mimetypes.guess_type(filename, False)
        if type is not None:
            response['content-type'] = type

        if encoding is not None:
            response['content-encoding'] = encoding

        response['content-disposition'] = 'attachment; filename=%s' % filename

        return response

    except Exception, e:
        return HttpResponseNotFound(json_error(e))


@validate_uri
def put(request):
    """
    Uploads a file to the supplied URI
    """
    import socket
    import httplib

    try:
        logger.debug("yabiusername: %s uri: %s" %(request.GET['yabiusername'], request.GET['uri']))
        uri = request.GET['uri']
        yabiusername = request.GET['yabiusername']
        
        resource = "%s?uri=%s" % (settings.YABIBACKEND_PUT, quote(uri))

        # TODO this only works with files written to disk by django
        # at the moment so the FILE_UPLOAD_MAX_MEMORY_SIZE must be set to 0
        # in settings.py
        files = []
        in_file = request.FILES['file1']
        files.append((in_file.name, in_file.name, in_file.temporary_file_path()))
        bc = get_backendcredential_for_uri(yabiusername, uri)
        logger.debug("files: %s"%repr(files))

        data=[]
        resource += "&username=%s&password=%s&cert=%s&key=%s"%(quote(bc.credential.username),quote(bc.credential.password),quote( bc.credential.cert),quote(bc.credential.key))
        h = post_multipart(settings.YABIBACKEND_SERVER, resource, data, files)
        return HttpResponse('ok')
        
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise


@validate_user
def submitworkflow(request):
    assert(request.POST['username'])
    logger.debug(request.POST['username'])

    workflow_json = request.POST["workflowjson"]
    workflow_dict = json.loads(workflow_json)
    user = User.objects.get(name=request.POST['username'])
    
    workflow = EngineWorkflow(name=workflow_dict["name"], json=workflow_json, user=user)
    workflow.save()

    # put the workflow in the store
    status, data = StoreHelper.updateWorkflow(workflow, workflow.json)
    assert(status == 200)
    
    # trigger a build via celery
    build.delay(workflow_id=workflow.id)

    return HttpResponse(json.dumps({"id":workflow.id}))

#@validate_user
def getuploadurl(request):
    if 'uri' not in request.REQUEST:
        return HttpResponseBadRequest("uri needs to be passed in\n")
    if 'yabiusername' not in request.REQUEST:
        return HttpResponseBadRequest("yabiusername needs to be passed in\n")
    
    yabiusername = request.REQUEST['yabiusername']
    uri = request.REQUEST['uri']
    
    uploadhash = str(uuid.uuid4())
        
    # now send this hash to the back end to inform it of the soon to be incomming upload
    upload_url = send_upload_hash(yabiusername,uri,uploadhash)
    
    # at the moment we can just return the URL for the backend upload. Todo. return a hash based URL
    #schema = "http"
    #host = request.META['SERVER_NAME']
    #port = int(request.META['SERVER_PORT'])
    #path = "/fs/put?uri=%s&yabiusername=%s"%(request.REQUEST['uri'], request.REQUEST['yabiusername'])
    
    return HttpResponse(
        json.dumps(upload_url)
    )
    
