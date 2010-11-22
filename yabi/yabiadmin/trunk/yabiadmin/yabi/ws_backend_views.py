# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import webhelpers
from django.utils import simplejson as json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from yabiadmin.yabi.models import User, ToolGrouping, ToolGroup, Tool, ToolParameter, Credential, Backend, ToolSet, BackendCredential
from yabiadmin.yabi.models import DecryptedCredentialNotAvailable
from yabiadmin.yabiengine import backendhelper
from yabiadmin.yabiengine.urihelper import uriparse

import logging
logger = logging.getLogger('yabiadmin')



def credential_uri(request, yabiusername):
    if 'uri' not in request.REQUEST:
        return HttpResponse("Request must contain parameter 'uri' in the GET or POST parameters.")
        
    uri = request.REQUEST['uri']
    logger.debug('yabiusername: %s uri: %s'%(yabiusername,uri))

    # parse the URI into chunks
    schema, rest = uriparse(uri)

    try:
        bc = backendhelper.get_backendcredential_for_uri(yabiusername, uri)
        return HttpResponse(bc.json())
    except ObjectDoesNotExist, odne:
        return HttpResponseNotFound("Object not found")
    except DecryptedCredentialNotAvailable, dcna:
        return HttpResponse("Decrypted Credential Not Available: %s"%dcna, status=503)
