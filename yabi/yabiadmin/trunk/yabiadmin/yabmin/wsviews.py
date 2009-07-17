from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from yabiadmin.yabmin.models import User, ToolGrouping, ToolGroup, Tool, ToolParameter, Credential, Backend, ToolSet, BackendCredential
from django.utils import webhelpers
try:
    from django.utils import simplejson as json
except ImportError:
    import json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from yabiadmin.yabiengine import wfbuilder

import logging
logger = logging.getLogger('yabmin')


def tool(request, toolname):

    try:
        tool = Tool.objects.get(name=toolname)
        return HttpResponse(tool.json())
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")


def menu(request, username):

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
                tool_dict = toolgroup.tool.tool_dict()
                tool["outputExtensions"] = toolgroup.tool.output_filetype_extensions()
                tool["inputExtensions"] = toolgroup.tool.input_filetype_extensions()


            # now add the toolgroups to toolsets
            for key, value in toolgroups.iteritems():
                ts["toolgroups"].append(value)


        return HttpResponse(json.dumps({"menu":output}))
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")    


def submitworkflow(request):
    logger.debug('submitworkflow')
    try:
        # probably want to catch the type of exceptions we may get from this
        wfbuilder.build(request.POST['username'], request.POST["workflowjson"])
        
        return HttpResponse(request.POST["workflowjson"])
    except KeyError,e:
        return HttpResponseNotFound(e.message)


def credential(request, username, backend):

    try:
        bc = BackendCredential.objects.get(backend__name=backend, credential__user__name=username)
        return HttpResponse(bc.json())
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")


def credential_detail(request, username, backend, detail):

    try:
        backend = Backend.objects.get(name=backend, credential__user__name=username)

        if detail == 'cert':
            return HttpResponse(backend.credential.cert)

        elif detail == 'key':
            return HttpResponse(backend.credential.key)

        elif detail == 'username':
            return HttpResponse(backend.credential.username)

        else:
            return HttpResponseNotFound("Object not found")            

    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")
