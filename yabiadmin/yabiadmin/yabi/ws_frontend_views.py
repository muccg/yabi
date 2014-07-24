# -*- coding: utf-8 -*-
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

import mimetypes
import os
import re
import itertools
from datetime import datetime, timedelta
from urllib import unquote
from urlparse import urlparse, urlunparse
from collections import OrderedDict

from django.db import transaction
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.http import HttpResponseNotAllowed, HttpResponseServerError, StreamingHttpResponse
from django.core.exceptions import ObjectDoesNotExist
from yabiadmin.yabi.models import User, ToolGrouping, Tool, ToolDesc, Credential, BackendCredential
from django.utils import simplejson as json
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from yabiadmin.backend.celerytasks import process_workflow
from yabiadmin.yabiengine.enginemodels import EngineWorkflow
from yabiadmin.yabiengine.models import WorkflowTag, SavedWorkflow
from yabiadmin.responses import *
from yabiadmin.decorators import authentication_required, profile_required
from yabiadmin.utils import cache_keyname, json_error_response, json_response
from yabiadmin.backend import backend
from yabiadmin.backend.exceptions import FileNotFoundError

import logging
logger = logging.getLogger(__name__)

DATE_FORMAT = '%Y-%m-%d'


@authentication_required
def tool(request, toolname, toolid=None):
    toolname_key = "%s-%s" % (cache_keyname(toolname), toolid or "")
    page = cache.get(toolname_key)

    if page:
        logger.debug("Returning cached page for tool:%s using key:%s " % (toolname, toolname_key))
        return page

    try:
        if toolid is None:
            tool = ToolDesc.objects.get(name=toolname)
        else:
            tool = Tool.objects.get(id=toolid, desc__name=toolname)

        response = HttpResponse(tool.json_pretty(), content_type="application/json; charset=UTF-8")
        cache.set(toolname_key, response, 30)
        return response
    except ObjectDoesNotExist:
        return JsonMessageResponseNotFound("Object not found")


@authentication_required
@cache_page(300)
@vary_on_cookie
def menu(request):
    # this view converts the tools into a form used by the front end.
    # ToolSets are not shown in the front end, but map users to groups
    # of tools.
    # ToolGroups are for example genomics, select data, mapreduce.
    toolset = menu_all_tools_toolset(request.user)
    return HttpResponse(json.dumps({"menu": {"toolsets": [toolset]}}),
                        content_type="application/json")


@authentication_required
def menu_saved_workflows(request):
    toolset = menu_saved_workflows_toolset(request.user)
    return HttpResponse(json.dumps({"menu": {"toolsets": [toolset]}}),
                        content_type="application/json")


def menu_all_tools_toolset(user):
    creds = BackendCredential.objects.filter(credential__user__user=user)
    backends = creds.values_list("backend", flat=True)
    user_tools = Tool.objects.filter(enabled=True, backend__in=backends,
                                     fs_backend__in=backends)

    qs = ToolGrouping.objects.filter(tool_set__users=user)
    qs = qs.filter(tool__in=user_tools.values_list("desc", flat=True))
    qs = qs.order_by("tool_group__name", "tool__name")
    qs = qs.select_related("tool_group", "tool")
    qs = qs.prefetch_related(
        'tool__tooloutputextension_set__file_extension',
        'tool__toolparameter_set__accepted_filetypes__extensions',
        'tool__tool_set',
    )

    all_tools = OrderedDict()
    for toolgroup in qs:
        tg = all_tools.setdefault(toolgroup.tool_group.name, OrderedDict())
        backend_tools = toolgroup.tool.tool_set.values_list("id", "backend__name")
        for backend_tool_id, backend_name in backend_tools:
            tg.setdefault(backend_tool_id, {
                "name": toolgroup.tool.name,
                "displayName": toolgroup.tool.display_name,
                "description": toolgroup.tool.description,
                "outputExtensions": toolgroup.tool.output_filetype_extensions(),
                "inputExtensions": toolgroup.tool.input_filetype_extensions(),
                "toolId": backend_tool_id,
                "backend": backend_name,
                "manyBackends": len(backend_tools) > 1,
            })

    return {
        "name": "all_tools",
        "toolgroups": [{"name": name, "tools": toolgroup.values()}
                       for name, toolgroup in all_tools.iteritems()]
    }


def menu_saved_workflows_toolset(user):
    def make_tool(wf):
        return {
            "name": wf.name,
            "savedWorkflowId": wf.id,
            "displayName": wf.name,
            "description": wf.creator.name,
            "creator": wf.creator.name,
            "created_on": str(wf.created_on),
            "json": json.loads(wf.json),
        }

    qs = SavedWorkflow.objects.filter(creator=user).order_by("created_on")
    qs = qs.select_related("creator")

    toolgroups = [{
        "name": "Saved Workflows",
        "tools": map(make_tool, qs),
    }]

    return {
        "name": "saved_workflows",
        "toolgroups": toolgroups
    }


@authentication_required
def ls(request):
    """
    This function will return a list of backends the user has access to IF the uri is empty. If the uri
    is not empty then it will pass on the call to the backend to get a listing of that uri
    """
    yabiusername = request.user.username
    logger.debug('yabiusername: {0} uri: {1}'.format(yabiusername, request.GET['uri']))
    if request.GET['uri']:
        recurse = request.GET.get('recurse')
        listing = backend.get_listing(yabiusername, request.GET['uri'], recurse is not None)
    else:
        listing = backend.get_backend_list(yabiusername)

    return HttpResponse(json.dumps(listing))


@authentication_required
def copy(request):
    """
    This function will instantiate a copy on the backend for this user
    """
    yabiusername = request.user.username

    src, dst = request.GET['src'], request.GET['dst']

    # check that src does not match dst
    srcpath, srcfile = src.rsplit('/', 1)
    assert srcpath != dst, "dst must not be the same as src"

    # src must not be directory
    assert src[-1] != '/', "src malformed. Either no length or not trailing with slash '/'"
    # TODO: This needs to be fixed in the FRONTEND, by sending the right url through as destination. For now we just make sure it ends in a slash
    if dst[-1] != '/':
        dst += '/'
    logger.debug("yabiusername: %s src: %s -> dst: %s" % (yabiusername, src, dst))

    backend.copy_file(yabiusername, src, dst)

    return HttpResponse("OK")


@authentication_required
def rcopy(request):
    """
    This function will instantiate a rcopy on the backend for this user
    """
    yabiusername = request.user.username

    src, dst = unquote(request.REQUEST['src']), unquote(request.REQUEST['dst'])

    # check that src does not match dst
    srcpath, srcfile = src.rstrip('/').rsplit('/', 1)
    assert srcpath != dst, "dst must not be the same as src"

    dst = os.path.join(dst, srcfile)

    # src must be directory
    # assert src[-1]=='/', "src malformed. Not directory."
    # TODO: This needs to be fixed in the FRONTEND, by sending the right url through as destination. For now we just make sure it ends in a slash
    if dst[-1] != '/':
        dst += '/'
    logger.debug("yabiusername: %s src: %s -> dst: %s" % (yabiusername, src, dst))

    backend.rcopy_file(yabiusername, src, dst)

    return HttpResponse("OK")


@authentication_required
def rm(request):
    yabiusername = request.user.username
    logger.debug("yabiusername: %s uri: %s" % (yabiusername, request.GET['uri']))
    backend.rm_file(yabiusername, request.GET['uri'])
    # TODO Forbidden, any other errors
    return HttpResponse("OK")


@authentication_required
def mkdir(request):
    backend.mkdir(request.user.username, request.GET['uri'])
    return HttpResponse("OK")


def backend_get_file(yabiusername, uri, is_dir=False):
    if is_dir:
        f, status_queue = backend.get_zipped_dir(yabiusername, uri)
    else:
        f, status_queue = backend.get_file(yabiusername, uri)

    CHUNKSIZE = 64 * 1024

    for chunk in iter(lambda: f.read(CHUNKSIZE), ""):
        yield chunk
    f.close()

    success = status_queue.get()

    if not success:
        raise Exception("Backend file download was not successful")


def filename_from_uri(uri, default='default.txt'):
    try:
        return uri.rstrip('/').rsplit('/', 1)[1]
    except IndexError:
        logger.critical('Unable to get filename from uri: %s' % uri)
        return default


@authentication_required
def get(request):
    """ Returns the requested uri.  """
    yabiusername = request.user.username

    logger.debug("ws_frontend_views::get() yabiusername: %s uri: %s" % (yabiusername, request.GET['uri']))
    uri = request.GET['uri']

    filename = filename_from_uri(uri)

    try:
        response = StreamingHttpResponse(backend_get_file(yabiusername, uri))
    except FileNotFoundError:
        response = HttpResponseNotFound()
    else:
        mimetypes.init([os.path.join(settings.WEBAPP_ROOT, 'mime.types')])
        mtype, file_encoding = mimetypes.guess_type(filename, False)
        if mtype is not None:
            response['content-type'] = mtype

        response['content-disposition'] = 'attachment; filename="%s"' % filename

    return response


@authentication_required
def zget(request):
    yabiusername = request.user.username

    logger.debug("ws_frontend_views::zget() yabiusername: %s uri: %s" % (yabiusername, request.GET['uri']))
    uri = request.GET['uri']

    filename = filename_from_uri(uri, default='default.tar.gz')

    try:
        response = StreamingHttpResponse(backend_get_file(yabiusername, uri, is_dir=True))
    except FileNotFoundError:
        response = HttpResponseNotFound()
    else:
        response['content-type'] = "application/x-gtar"
        response['content-disposition'] = 'attachment; filename="%s.tar.gz"' % filename

    return response


@authentication_required
def put(request):
    """
    Uploads a file to the supplied URI

    NB: if anyone changes FILE_UPLOAD_MAX_MEMORY_SIZE in the settings to be greater than zero
    this function will not work as it calls temporary_file_path
    """
    yabiusername = request.user.username

    logger.debug("uri: %s" % request.GET['uri'])
    uri = request.GET['uri']

    num_success = 0
    num_fail = 0

    for key, f in request.FILES.items():
        upload_handle, status_queue = backend.put_file(yabiusername, f.name, uri)
        for chunk in f.chunks():
            upload_handle.write(chunk)
        upload_handle.close()

        if status_queue.get():
            num_success += 1
        else:
            num_fail += 1

    response = {
        "level": "success" if num_fail == 0 else "failure",
        "num_success": num_success,
        "num_fail": num_fail,
        "message": 'no message'
    }

    return HttpResponse(content=json.dumps(response))


@authentication_required
@transaction.commit_manually
def submit_workflow(request):
    try:
        received_json = request.POST["workflowjson"]
        workflow_dict = json.loads(received_json)

        yabiuser = User.objects.get(name=request.user.username)

        # Check if the user already has a workflow with the same name, and if so,
        # munge the name appropriately.
        workflow_dict["name"] = munge_name(yabiuser.workflow_set, workflow_dict["name"])
        workflow_json = json.dumps(workflow_dict)

        workflow = EngineWorkflow.objects.create(
            name=workflow_dict["name"],
            user=yabiuser,
            json=workflow_json,
            original_json=received_json,
            start_time=datetime.now()
        )

        # always commit transactions before sending tasks depending on state from the current transaction
        # http://docs.celeryq.org/en/latest/userguide/tasks.html
        transaction.commit()

        # process the workflow via celery
        process_workflow(workflow.pk).apply_async()
    except Exception:
        transaction.rollback()
        logger.exception("Exception in submit_workflow()")
        return json_error_response("Workflow submission error")

    return json_response({"workflow_id": workflow.pk})


def munge_name(workflow_set, workflow_name):
    if not workflow_set.filter(name=workflow_name).exists():
        return workflow_name

    match = re.search(r"^(.*) \(([0-9]+)\)$", workflow_name)
    base = match.group(1) if match else workflow_name

    workflows = workflow_set.filter(name__startswith=base)
    used_names = frozenset(workflows.values_list("name", flat=True))

    unused_name = lambda name: name not in used_names
    infinite_range = itertools.count

    generate_unique_names = ("%s (%d)" % (base, i) for i in infinite_range(1))
    next_available_name = find_first(unused_name, generate_unique_names)

    return next_available_name


@authentication_required
def save_workflow(request):
    try:
        workflow_dict = json.loads(request.POST["workflowjson"])
    except KeyError:
        return json_error_response("workflowjson param not posted",
                                   status=400)
    except ValueError:
        return json_error_response("Invalid workflow JSON")

    yabiuser = User.objects.get(name=request.user.username)

    # Check if the user already has a workflow with the same name, and if so,
    # munge the name appropriately.
    workflow_dict["name"] = munge_name(yabiuser.savedworkflow_set,
                                       workflow_dict["name"])
    workflow_json = json.dumps(workflow_dict)
    workflow = SavedWorkflow.objects.create(
        name=workflow_dict["name"],
        creator=yabiuser, created_on=datetime.now(),
        json=workflow_json
    )

    return json_response({"saved_workflow_id": workflow.pk})


@authentication_required
def delete_saved_workflow(request):
    if "id" not in request.POST:
        return HttpResponseBadRequest("Need id param")

    workflow = get_object_or_404(SavedWorkflow, id=request.POST["id"])

    if workflow.creator.user != request.user and not request.user.is_superuser:
        return json_error_response("That's not yours", status=403)

    workflow.delete()

    return json_response("deleted")


@authentication_required
@cache_page(20)
def get_workflow(request, workflow_id):
    yabiusername = request.user.username
    logger.debug(yabiusername)

    if not (workflow_id and yabiusername):
        return JsonMessageResponseNotFound('No workflow_id or no username supplied')

    workflow_id = int(workflow_id)
    workflows = EngineWorkflow.objects.filter(id=workflow_id)
    if len(workflows) != 1:
        msg = 'Workflow %d not found' % workflow_id
        logger.critical(msg)
        return JsonMessageResponseNotFound(msg)

    response = workflow_to_response(workflows[0])

    return HttpResponse(json.dumps(response),
                        mimetype='application/json')


def workflow_to_response(workflow, parse_json=True, retrieve_tags=True):
    fmt = DATE_FORMAT
    response = {
        'id': workflow.id,
        'name': workflow.name,
        'last_modified_on': workflow.last_modified_on.strftime(fmt),
        'created_on': workflow.created_on.strftime(fmt),
        'status': workflow.status,
        'is_retrying': workflow.is_retrying,
        'json': json.loads(workflow.json) if parse_json else workflow.json,
        'tags': [],
    }

    if retrieve_tags:
        response["tags"] = [wft.tag.value for wft in workflow.workflowtag_set.all()]

    return response


@authentication_required
def workflow_datesearch(request):
    if request.method != 'GET':
        return JsonMessageResponseNotAllowed(["GET"])

    yabiusername = request.user.username
    logger.debug(yabiusername)

    fmt = DATE_FORMAT
    tomorrow = lambda: datetime.today() + timedelta(days=1)

    start = datetime.strptime(request.GET['start'], fmt)
    end = request.GET.get('end')
    if end is None:
        end = tomorrow()
    else:
        end = datetime.strptime(end, fmt)
    sort = request.GET['sort'] if 'sort' in request.GET else '-created_on'

    # Retrieve the matched workflows.
    workflows = EngineWorkflow.objects.filter(
        user__name=yabiusername,
        created_on__gte=start, created_on__lte=end
    ).order_by(sort)

    # Use that list to retrieve all of the tags applied to those workflows in
    # one query, then build a dict we can use when iterating over the
    # workflows.
    workflow_tags = WorkflowTag.objects.select_related("tag", "workflow").filter(workflow__in=workflows)
    tags = {}
    for wt in workflow_tags:
        tags.setdefault(wt.workflow.id, []).append(wt.tag.value)

    response = []
    for workflow in workflows:
        workflow_response = workflow_to_response(workflow, parse_json=False, retrieve_tags=False)
        workflow_response["tags"] = tags.get(workflow.id, [])
        response.append(workflow_response)

    return HttpResponse(json.dumps(response), mimetype='application/json')


@authentication_required
def workflow_change_tags(request, id=None):
    if request.method != 'POST':
        return JsonMessageResponseNotAllowed(["POST"])
    id = int(id)

    yabiusername = request.user.username
    logger.debug(yabiusername)

    if 'taglist' not in request.POST:
        return HttpResponseBadRequest("taglist needs to be passed in\n")

    taglist = request.POST['taglist'].split(',')
    taglist = [t.strip() for t in taglist if t.strip()]
    try:
        workflow = EngineWorkflow.objects.get(pk=id)
    except EngineWorkflow.DoesNotExist:
        return HttpResponseNotFound()

    workflow.change_tags(taglist)

    return HttpResponse("Success")


@authentication_required
@profile_required
def passchange(request):
    if request.method != "POST":
        return HttpResponseNotAllowed("Method must be POST")

    profile = request.user.get_profile()
    success, message = profile.passchange(request)
    if success:
        return HttpResponse(json.dumps(message))
    else:
        return HttpResponseServerError(json.dumps(message))


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
    # replace all of the fields, since this
    # service can only create unencrypted credentials at present.
    if "password" in request.POST or "key" in request.POST or "certificate" in request.POST:
        credential.password = request.POST.get("password", "")
        credential.key = request.POST.get("key", "")
        credential.cert = request.POST.get("certificate", "")

    if "username" in request.POST:
        credential.username = request.POST["username"]

    credential.save()

    return JsonMessageResponse("Credential updated successfully")


def find_first(pred, sequence):
    for x in sequence:
        if pred(x):
            return x
