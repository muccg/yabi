from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
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

def credential(request, yabiusername, scheme, username, hostname):
    logger.debug('Credential request for yabiusername: %s scheme: %s username: %s hostname: %s' % (yabiusername, scheme, username, hostname))
    
    try:
        bc = BackendCredential.objects.get(credential__user__name=yabiusername,
                                           backend__scheme=scheme,
                                           credential__username=username,
                                           backend__hostname=hostname)
        logger.debug("returning bc... %s" % bc)
        return HttpResponse(bc.json())

    except (ObjectDoesNotExist, MultipleObjectsReturned):
        logger.critical('Invalid backend credential found for yabiusername: %s scheme: %s hostname: %s username: %s' % (yabiusername, scheme, hostname, username))
        return HttpResponseNotFound("Object not found")



def credential_detail(request, yabiusername, scheme, username, hostname, detail):
    logger.debug('')
    
    try:
        bc = BackendCredential.objects.get(credential__user__name=yabiusername,
                                           backend__scheme=scheme,
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

    except (ObjectDoesNotExist, MultipleObjectsReturned):
        logger.critical('Invalid backend credential found for yabiusername: %s scheme: %s hostname: %s username: %s' % (yabiusername, scheme, hostname, username))
        return HttpResponseNotFound("Object not found")
