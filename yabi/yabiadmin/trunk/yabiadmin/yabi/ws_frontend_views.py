# -*- coding: utf-8 -*-
import mimetypes
import uuid

from urllib import quote

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from yabiadmin.yabi.models import User, ToolGrouping, ToolGroup, Tool, ToolParameter, Credential, Backend, ToolSet, BackendCredential
from django.utils import webhelpers
from django.utils import simplejson as json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.conf import settings

from yabiadmin.yabiengine import storehelper as StoreHelper
from yabiadmin.yabiengine.tasks import build
from yabiadmin.yabiengine.enginemodels import EngineWorkflow
from yabiadmin.yabiengine.backendhelper import get_listing, get_backend_list, get_file, get_backendcredential_for_uri, copy_file, rm_file, send_upload_hash
from yabiadmin.utils import json_error
from yabi.file_upload import *
from django.contrib import auth
from decorators import memcache, authentication_required


import logging
logger = logging.getLogger('yabiadmin')



## TODO do we want to limit tools to those the user can access?
## will need to change call from front end to include username
## then uncomment decorator

def login(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    username = request.POST.get('username')
    password = request.POST.get('password')
    if not (username and password):
        return HttpResponseBadRequest()
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            response = {
                "success": True
            }
        else:
            response = {
                "success": False,
                "message": "The account has been disabled.",
            }
    else:
        response = {
            "success": False,
            "message": "The user name and password are incorrect.",
        }
    return HttpResponse(content=json.dumps(response))

def logout(request):
    auth.logout(request)
    response = {
        "success": True,
    }
    return HttpResponse(content=json.dumps(response))

@authentication_required
@memcache("tool",timeout=30,refresh=True,user_specific=False)
def tool(request, *args, **kwargs):
    toolname = kwargs['toolname']
    logger.debug(toolname)

    try:
        tool = Tool.objects.get( name=toolname )
        return HttpResponse(tool.json())
    except ObjectDoesNotExist:
        return HttpResponseNotFound(json_error("Object not found"))



@authentication_required
@memcache("menu",timeout=300)
def menu(request):
    username = request.user.username
    logger.debug('Username: ' + username)

    try:
        all_tools = {}
        toolsets = ToolSet.objects.filter(users__name=username)
        for toolset in toolsets:
            for toolgroup in ToolGrouping.objects.filter(tool_set=toolset):
                tg = all_tools.setdefault(toolgroup.tool_group.name, {})
                tool = tg.setdefault(toolgroup.tool.name, {})
                if not tool:
                    tool["name"] = toolgroup.tool.name
                    tool["displayName"] = toolgroup.tool.display_name
                    tool["description"] = toolgroup.tool.description                
                    tool["outputExtensions"] = toolgroup.tool.output_filetype_extensions()
                    tool["inputExtensions"] = toolgroup.tool.input_filetype_extensions()


        # from here down is getting the tools into a form
        # used by the front end so no changes are needed there
        # toolsets are dev, marine science, ccg etc, not used on the front end
        # toolgroups are for example genomics, select data, mapreduce        

        output = {}
        output['menu'] = {}
        output['menu']['toolsets'] = []

        all_tools_toolset = {}
        output['menu']['toolsets'].append(all_tools_toolset)

        all_tools_toolset["name"] = 'all_tools'
        all_tools_toolset["toolgroups"] = []


        for key, toolgroup in all_tools.iteritems():
            tg = {}
            tg['name'] = key
            tg['tools'] = []

            for toolname, tool in toolgroup.iteritems():
                tg['tools'].append(tool)

            all_tools_toolset["toolgroups"].append(tg)

        return HttpResponse(json.dumps(output))
    except ObjectDoesNotExist:
        return HttpResponseNotFound(json_error("Object not found"))

    
    
@authentication_required
def ls(request):
    """
    This function will return a list of backends the user has access to IF the uri is empty. If the uri
    is not empty then it will pass on the call to the backend to get a listing of that uri
    """
    yabiusername = request.user.username

    try:
        logger.debug("yabiusername: %s uri: %s" %(yabiusername, request.GET['uri']))
        if request.GET['uri']:
            filelisting = get_listing(yabiusername, request.GET['uri'])
        else:
            filelisting = get_backend_list(yabiusername)

        return HttpResponse(filelisting)
    except Exception, e:
        return HttpResponseNotFound(json_error(e))


@authentication_required
def copy(request):
    """
    This function will instantiate a copy on the backend for this user
    """
    yabiusername = request.user.username
    try:
        logger.debug("yabiusername: %s src: %s -> dst: %s" %(yabiusername, request.GET['src'],request.GET['dst']))
        status, data = copy_file(yabiusername,request.GET['src'],request.GET['dst'])

        return HttpResponse(content=data, status=status)
    except Exception, e:
        return HttpResponseNotFound(json_error(e))

@authentication_required
def rm(request):
    """
    This function will return a list of backends the user has access to IF the uri is empty. If the uri
    is not empty then it will pass on the call to the backend to get a listing of that uri
    """
    yabiusername = request.user.username
    try:
        logger.debug("yabiusername: %s uri: %s" %(yabiusername, request.GET['uri']))
        status, data = rm_file(yabiusername,request.GET['uri'])

        return HttpResponse(content=data, status=status)
    except Exception, e:
        return HttpResponseNotFound(json_error(e))


@authentication_required
def get(request):
    """
    Returns the requested uri. get_file returns an httplib response wrapped in a FileIterWrapper. This can then be read
    by HttpResponse
    """
    yabiusername = request.user.username
    try:
        logger.debug("yabiusername: %s uri: %s" %(yabiusername, request.GET['uri']))
        uri = request.GET['uri']
        
        try:
            filename = uri.rsplit('/', 1)[1]
        except IndexError, e:
            logger.critical('Unable to get filename from uri: %s' % uri)
            filename = 'default.txt'

        response = HttpResponse(get_file(yabiusername, uri))

        mimetypes.init([os.path.normpath(os.path.expanduser('~/.yabi/mime.types')), os.path.normpath('/etc/yabi/mime.types')])
        mtype, file_encoding = mimetypes.guess_type(filename, False)
        if mtype is not None:
            response['content-type'] = mtype

        response['content-disposition'] = 'attachment; filename=%s' % filename

        return response

    except Exception, e:
        return HttpResponseNotFound(json_error(e))


@authentication_required
def put(request):
    """
    Uploads a file to the supplied URI
    """
    import socket
    import httplib

    yabiusername = request.user.username
    try:
        logger.debug("yabiusername: %s uri: %s" %(yabiusername, request.REQUEST['uri']))
        uri = request.REQUEST['uri']
        
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


@authentication_required
def submitworkflow(request):
    yabiusername = request.user.username
    logger.debug(yabiusername)

    workflow_json = request.POST["workflowjson"]
    workflow_dict = json.loads(workflow_json)
    user = User.objects.get(name=yabiusername)
    
    workflow = EngineWorkflow(name=workflow_dict["name"], json=workflow_json, user=user)
    workflow.save()

    # put the workflow in the store
    from yabiadmin.yabistoreapp import db
    db.save_workflow(user.name, workflow.workflow_id, workflow_json, workflow.status, workflow.name)
    logger.debug("db.save_workflow(%s,%s,%s,%s,%s)"%(user.name,workflow.workflow_id, json, workflow.status, workflow.name))
    
    # trigger a build via celery
    build.delay(workflow_id=workflow.id)

    return HttpResponse(json.dumps({"id":workflow.id}))

#@authentication_required
def getuploadurl(request):
    raise Exception, "test explosion"
    
    if 'uri' not in request.REQUEST:
        return HttpResponseBadRequest("uri needs to be passed in\n")
    
    yabiusername = request.user.username
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
    
