# -*- coding: utf-8 -*-
import mimetypes
import uuid

from datetime import datetime, timedelta
from urllib import quote
from urlparse import urlparse, urlunparse

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseServerError, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from yabiadmin.yabi.models import User, ToolGrouping, ToolGroup, Tool, ToolParameter, Credential, Backend, ToolSet, BackendCredential
from yabiadmin.yabi.models import DecryptedCredentialNotAvailable
from django.utils import webhelpers
from django.utils import simplejson as json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.ldap_helper import LDAPSearchResult, LDAPHandler
from django.conf import settings

from yabiadmin.yabiengine import storehelper as StoreHelper
from yabiadmin.yabiengine.tasks import build
from yabiadmin.yabiengine.enginemodels import EngineWorkflow
from yabiadmin.yabiengine.backendhelper import get_listing, get_backend_list, get_file, get_backendcredential_for_uri, copy_file, rm_file, send_upload_hash
from yabiadmin.responses import *
from yabi.file_upload import *
from django.contrib import auth
from yabiadmin.decorators import memcache, authentication_required


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
        return HttpResponse(tool.json_pretty(), content_type="text/plain; charset=UTF-8")
    except ObjectDoesNotExist:
        return JsonMessageResponseNotFound("Object not found")



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
        return JsonMessageResponseNotFound("Object not found")

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
    except DecryptedCredentialNotAvailable, dcna:
        return JsonMessageResponseServerError(dcna)
    except AssertionError, e:
        # The file handling functions in the backendhelper module throw
        # assertion errors when they receive an unexpected HTTP status code
        # from the backend. Since failed assertions don't result in the
        # exception having a useful message, we'll intercept it here and return
        # a response with something a little more useful for the user.
        return JsonMessageResponseNotFound("The requested directory either doesn't exist or is inaccessible")
    except Exception, e:
        return JsonMessageResponseNotFound(e)


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
    except AssertionError, e:
        # The file handling functions in the backendhelper module throw
        # assertion errors when they receive an unexpected HTTP status code
        # from the backend. Since failed assertions don't result in the
        # exception having a useful message, we'll intercept it here and return
        # a response with something a little more useful for the user.
        return JsonMessageResponseNotFound("The requested copy operation failed: please check that both the source file and destination exist and are accessible")
    except Exception, e:
        return JsonMessageResponseNotFound(e)

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
    except AssertionError, e:
        # The file handling functions in the backendhelper module throw
        # assertion errors when they receive an unexpected HTTP status code
        # from the backend. Since failed assertions don't result in the
        # exception having a useful message, we'll intercept it here and return
        # a response with something a little more useful for the user.
        return JsonMessageResponseNotFound("The requested file or directory is inaccessible and cannot be deleted")
    except Exception, e:
        return JsonMessageResponseNotFound(e)


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

        bytes = request.GET.get("bytes", None)
        if bytes is not None:
            try:
                bytes = int(bytes)
            except ValueError:
                bytes = None

        response = HttpResponse(get_file(yabiusername, uri, bytes=bytes))

        mimetypes.init([os.path.normpath('/usr/local/etc/mime.types')])
        mtype, file_encoding = mimetypes.guess_type(filename, False)
        if mtype is not None:
            response['content-type'] = mtype

        response['content-disposition'] = 'attachment; filename=%s' % filename

        return response

    except Exception, e:
        # The response from this view is displayed directly to the user, so
        # we'll send a normal response rather than a JSON message.
        raise Http404


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

        data = {
            "message": "Upload successful",
            "level": "success",
            "uri": uri,
        }

        return HttpResponse(content=json.dumps(data), content_type="text/plain; charset=UTF-8")
        
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise
    except KeyError, e:
        data = {
            "message": "No files uploaded",
            "level": "fail",
            "uri": uri,
        }

        return HttpResponse(content=json.dumps(data), content_type="text/plain; charset=UTF-8")
        
        return JsonMessageResponseBadRequest("No files uploaded")


@authentication_required
def submitworkflow(request):
    yabiusername = request.user.username
    logger.debug(yabiusername)

    workflow_json = request.POST["workflowjson"]
    workflow_dict = json.loads(workflow_json)
    user = User.objects.get(name=yabiusername)
    
    workflow = EngineWorkflow(name=workflow_dict["name"], user=user)
    workflow.save()

    # put the workflow in the store
    workflow.json = workflow_json
    
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


@authentication_required
def credential(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    yabiuser = User.objects.get(name=request.user.username)
    creds = Credential.objects.filter(user=yabiuser)

    exists = lambda value: value is not None and len(value) > 0

    def backends(credential):
        backend_credentials = BackendCredential.objects.filter(credential=credential)
        backends = []

        for bc in backend_credentials:
            # Build up the display URI for the backend, which may include the
            # home directory and username in addition to the backend URI
            # proper.
            if bc.homedir:
                uri = bc.backend.uri + bc.homedir
            else:
                uri = bc.backend.uri

            scheme, netloc, path, params, query, fragment = urlparse(uri)

            # Add the credential username if the backend URI doesn't already
            # include one.
            if "@" not in netloc:
                netloc = "%s@%s" % (credential.username, netloc)

            backends.append(urlunparse((scheme, netloc, path, params, query, fragment)))

        return backends

    def expires_in(expires_on):
        if expires_on is not None:
            # Unfortunately, Python's timedelta class doesn't provide a simple way
            # to get the number of seconds total out of it.
            delta = expires_on - datetime.now()
            return (delta.days * 86400) + delta.seconds
        
        return None

    return HttpResponse(json.dumps([{
        "id": c.id,
        "description": c.description,
        "username": c.username,
        "password": exists(c.password),
        "certificate": exists(c.cert),
        "key": exists(c.key),
        "backends": backends(c),
        "expires_in": expires_in(c.expires_on),
        "encrypted": c.encrypted,
    } for c in creds]), content_type="application/json; charset=UTF-8")


@authentication_required
def save_credential(request, id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        credential = Credential.objects.get(id=id)
        yabiuser = User.objects.get(name=request.user.username)
    except Credential.DoesNotExist:
        return JsonMessageResponseNotFound("Credential ID not found")
    except User.DoesNotExist:
        return JsonMessageResponseNotFound("User not found")

    if credential.user != yabiuser:
        return JsonMessageResponseForbidden("User does not have access to the given credential")

    # Special case: if we're only updating the expiry, we should do that first,
    # since we can do that without unencrypting encrypted credentials.
    if "expiry" in request.POST:
        if request.POST["expiry"] == "never":
            credential.expires_on = None
        else:
            try:
                credential.expires_on = datetime.now() + timedelta(seconds=int(request.POST["expiry"]))
            except TypeError:
                return JsonMessageResponseBadRequest("Invalid expiry")

    # OK, let's see if we have any of password, key or certificate. If so, we
    # replace all of the fields and clear the encrypted flag, since this
    # service can only create unencrypted credentials at present.
    if "password" in request.POST or "key" in request.POST or "certificate" in request.POST:
        credential.encrypted = False
        credential.password = request.POST.get("password", "")
        credential.key = request.POST.get("key", None)
        credential.cert = request.POST.get("certificate", None)

    if "username" in request.POST:
        credential.username = request.POST["username"]

    credential.save()

    return JsonMessageResponse("Credential updated successfully")
