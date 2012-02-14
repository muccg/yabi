# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from ccg.utils import webhelpers
from django.utils import simplejson as json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from yabiadmin.yabi.models import User, ToolGrouping, ToolGroup, Tool, ToolParameter, Credential, Backend, ToolSet, BackendCredential
from yabiadmin.yabi.models import DecryptedCredentialNotAvailable
from yabiadmin.yabiengine import backendhelper
from yabiadmin.yabiengine.urihelper import uriparse
from yabiadmin.responses import *

from yabiadmin.decorators import memcache, authentication_required, profile_required, hmac_authenticated

import logging
logger = logging.getLogger(__name__)

#@authentication_required
@hmac_authenticated
def fs_credential_uri(request, yabiusername):
    if 'uri' not in request.REQUEST:
        return HttpResponse("Request must contain parameter 'uri' in the GET or POST parameters.")
        
    uri = request.REQUEST['uri']
    logger.debug('yabiusername: %s uri: %s'%(yabiusername,uri))

    # parse the URI into chunks
    schema, rest = uriparse(uri)

    try:
        bc = backendhelper.get_fs_backendcredential_for_uri(yabiusername, uri)
        return HttpResponse(bc.json())
    except ObjectDoesNotExist, odne:
        return JsonMessageResponseNotFound("Object not found")
    except DecryptedCredentialNotAvailable, dcna:
        return JsonMessageResponseServerError("Decrypted Credential Not Available: %s" % dcna, status=503)

@hmac_authenticated
def exec_credential_uri(request, yabiusername):
    if 'uri' not in request.REQUEST:
        return HttpResponse("Request must contain parameter 'uri' in the GET or POST parameters.")
        
    uri = request.REQUEST['uri']
    logger.debug('yabiusername: %s uri: %s'%(yabiusername,uri))

    # parse the URI into chunks
    schema, rest = uriparse(uri)

    try:
        bc = backendhelper.get_exec_backendcredential_for_uri(yabiusername, uri)
        return HttpResponse(bc.json())
    except ObjectDoesNotExist, odne:
        return JsonMessageResponseNotFound("Object not found")
    except DecryptedCredentialNotAvailable, dcna:
        return JsonMessageResponseServerError("Decrypted Credential Not Available: %s" % dcna, status=503)

def backend_connection_limit(request,scheme,hostname):
    filt = Q(scheme=scheme) & Q(hostname=hostname)
    if 'port' in request.REQUEST:
        if request.REQUEST['port'].lower() == 'none':
            filt &= Q(port=None)
        else:
            filt &= Q(port=int(request.REQUEST['port']))
    if 'path' in request.REQUEST:
        filt &= Q(path=request.REQUEST['path'])
            
    backends = Backend.objects.filter(filt)
    if not len(backends):
        return HttpResponse("Object not found",status=404)
    if len(backends)>1:
        return HttpResponse("More than one matching backend object found",status=500)
    return HttpResponse(json.dumps(backends[0].max_connections))
