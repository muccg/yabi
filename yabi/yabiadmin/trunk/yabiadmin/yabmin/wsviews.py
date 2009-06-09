from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.db import connection
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from yabiadmin.yabmin.models import User, ToolGrouping, ToolGroup, Tool, ToolParameter, Credential, Backend, ToolSet
from yabiadmin import ldaputils
from django.utils import webhelpers
from django.utils import simplejson as json
from json_util import makeJsonFriendly
from django.contrib.auth.decorators import login_required


def tool(request, toolname):

    try:
        tool = Tool.objects.get(name=toolname)
        return HttpResponse(tool.json())
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")

def toollist(request, username):

    try:
        toolsets = ToolSet.objects.filter(users__name=username)

        output = {"toolsets":[]}

        for toolset in toolsets:


            ts = {}
            output["toolsets"].append(ts)
            ts["name"] = toolset.name
            ts["toolgroups"] = {}

            i = 1
            for toolgroup in ToolGrouping.objects.filter(tool_set=toolset):
                tg = {}
                if not toolgroup.tool_group.name in ts["toolgroups"]:
                    tg = {}
                    ts["toolgroups"][toolgroup.tool_group.name] = tg
                else:
                    tg = ts["toolgroups"][toolgroup.tool_group.name]

                if not "name" in tg:
                    tg["name"] = toolgroup.tool_group.name
                if not "tools" in tg:
                    tg["tools"] = []

                tool = {}
                tool["name"] = toolgroup.tool.name
                tool["displayname"] = toolgroup.tool.display_name
                tool["description"] = toolgroup.tool.description                
                tg["tools"].append(tool)
                tool_dict = toolgroup.tool.tool_dict()
                tool["output_filetypes"] = tool_dict["output_filetypes"]

#                for tool in Tool.objects.filter(


##            ts = {}
##            ts["toolset"] = toolsetname
##            ts["toolgroups"] = []

##            ts["toolgroups"] = []

##            toolgroup = {}
##            toolgroup["toolgroup_name"] = tg.tool_group.name
##            toolgroup["tools"] = []

##            tool = {}
##            if tg.tool_group.name not in ts:
##                output[tg.tool_group.name] = []
##            output[tg.tool_group.name].append({'name':tg.tool.name, 'displayname':tg.tool.display_name})




##            # add toolset level
##            if toolsetname not in output["toolsets"]:
##                output["toolsets"].append(ts)
            


        return HttpResponse(json.dumps({"menu":output}))
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")    



##{"toolGroups": [ {"groupName":"EMBOSS", "items": [ {"description":"Produces a file containing codon usage statistics. Accepts: fa,fna,faa,seq Outputs: out",
##"toolName":"chips",
##"inputFiletypes":[ {"extension":"fa"}, {"extension":"fna"}, {"extension":"faa"}, {"extension":"seq"}, ],
##"displayName":"chips",
##"outputFiletypes":[ {"extension":"out"}, ] },



def credential(request, username, backend):

    try:
        backend = Backend.objects.get(name=backend, credential__user__name=username)
        return HttpResponse(backend.json())
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
