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

import logging
import yabilogging
logger = logging.getLogger('yabiadmin')

def credential(request, scheme, username, hostname):
    logger.debug('Credential request for scheme: %s username: %s hostname: %s' % (scheme, username, hostname))
    
    try:
        bc = BackendCredential.objects.get(backend__scheme=scheme,
                                           credential__username=username,
                                           backend__hostname=hostname)
        return HttpResponse(bc.json())

    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")


def credential_detail(request, scheme, username, hostname):
    logger.debug('')
    
    try:
        bc = BackendCredential.objects.get(backend__scheme=scheme,
                                           credential__username=username,
                                           backend__hostname=hostname)


        if detail == 'cert':
            return HttpResponse(bc.credential.cert)

        elif detail == 'key':
            return HttpResponse(bc.credential.key)

        elif detail == 'username':
            return HttpResponse(bc.credential.username)

        else:
            return HttpResponseNotFound("Object not found")            

    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")
