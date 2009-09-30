from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from yabiadmin.yabmin.models import User, ToolGrouping, ToolGroup, Tool, ToolParameter, Credential, Backend, ToolSet, BackendCredential
from django.utils import webhelpers
from django.utils import simplejson as json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.conf import settings
from yabiadmin.yabiengine import wfbuilder
from yabiadmin.yabiengine import backendhelper
from yabiadmin.security import validate_user, validate_uri
from yabiadmin.utils import json_error


from yabmin.file_upload import *

import logging
import yabilogging
logger = logging.getLogger('yabiadmin')

## TODO do we want to limit tools to those the user can access?
def tool(request, toolname):
    logger.debug('')

    try:
        tool = Tool.objects.get(name=toolname)
        return HttpResponse(tool.json())
    except ObjectDoesNotExist:
        return HttpResponseNotFound(json_error("Object not found"))


@validate_user
def menu(request, *args, **kwargs):
    logger.debug('')

    username = kwargs["username"]
    
    try:
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


        return HttpResponse(json.dumps({"menu":output}))
    except ObjectDoesNotExist:
        return HttpResponseNotFound(json_error("Object not found"))    


@validate_uri
def ls(request):
    """
    This function will return a list of backends the user has access to IF the uri is empty. If the uri
    is not empty then it will pass on the call to the backend to get a listing of that uri
    """
    logger.debug('')

    try:
        if request.GET['uri']:
            filelisting = backendhelper.get_listing(request.GET['uri'])
        else:
            filelisting = backendhelper.get_backend_list(request.GET['yabiusername'])

        return HttpResponse(filelisting)
    except Exception, e:
        return HttpResponseNotFound(json_error(e))



@validate_uri
def put(request):
    """
    Uploads a file to the supplied URI
    """
    logger.debug('')

    import socket
    import httplib

    try:
        resource = "%s?uri=%s" % (settings.YABIBACKEND_PUT, request.GET['uri'])

        # TODO this only works with files written to disk by django
        # at the moment so the FILE_UPLOAD_MAX_MEMORY_SIZE must be set to 0
        # in settings.py
        files = []
        in_file = request.FILES['file1']
        files.append((in_file.name, in_file.name, in_file.temporary_file_path()))
        logger.debug(files)
        h = post_multipart(settings.YABIBACKEND_SERVER, resource, [], files)
        return HttpResponse('ok')
        
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise


























@validate_user
def submitworkflow(request):
    logger.debug('')
    
    try:
        # probably want to catch the type of exceptions we may get from this
        wfbuilder.build(request.POST['username'], request.POST["workflowjson"])
        
        return HttpResponse(request.POST["workflowjson"])
    except KeyError,e:
        return HttpResponseNotFound(json_error(e))
    except Exception,e:
        return HttpResponseNotFound(json_error(e))

