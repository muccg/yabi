# -*- coding: utf-8 -*-
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
from yabiadmin.yabiengine.urihelper import uriparse

import logging
logger = logging.getLogger('yabiadmin')



def credential_uri(request, yabiusername):
    if 'uri' not in request.REQUEST:
        return HttpResponse("Request must contain parameter 'uri' in the GET or POST parameters.")
        
    uri = request.REQUEST['uri']
    logger.debug('credential request for yabiusername: %s uri: %s'%(yabiusername,uri))

    # parse the URI into chunks
    schema, rest = uriparse(uri)

    logger.debug('uriparse returned... yabiusername: %s schema:%s username:%s hostname:%s path:%s'%(yabiusername,schema,rest.username,rest.hostname,rest.path))

    # get our set of credential candidates
    #bcs = BackendCredential.objects.filter(credential__user__name=yabiusername,
                                           #backend__scheme=schema,
                                           #credential__username=rest.username,
                                           #backend__hostname=rest.hostname)
    bcs = BackendCredential.objects.filter(credential__user__name=yabiusername,
                                           backend__hostname=rest.hostname)
    logger.debug("bc search found... >%s<" % (",".join([str(x) for x in bcs])))
    return HttpResponseNotFound("Object not found")

def credential_detail_uri(request, yabiusername, detail):
    logger.critical("Deprecated credential_detail call")
    
    uri = request.REQUEST['uri']
    logger.debug('credential request for yabiusername: %s uri: %s'%(yabiusername,uri))
    
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


def credential(request, yabiusername, scheme, username, hostname):
    logger.critical("Deprecated credential call")
    assert False, "Deprecated credential call"
    
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
    logger.critical("Deprecated credential_detail call")
    assert False, "Deprecated credential call"
    
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
