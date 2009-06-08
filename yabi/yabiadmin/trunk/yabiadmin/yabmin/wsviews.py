from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.db import connection
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from yabiadmin.yabmin.models import User, ToolGrouping, ToolGroup, Tool, ToolParameter, Credential, Backend
from yabiadmin import ldaputils
from django.utils import webhelpers
import simplejson as json
from json_util import makeJsonFriendly
from django.contrib.auth.decorators import login_required


def tool(request, toolname):

    try:
        tool = Tool.objects.get(name=toolname)
        return HttpResponse(tool.json())
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")


def credential(request, username, backend):

    try:
        backend = Backend.objects.get(name=backend, credential__user__name=username)
        return HttpResponse(backend.json())
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")

