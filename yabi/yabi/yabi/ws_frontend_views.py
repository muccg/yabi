# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
import json
import mimetypes
import os
import re
import itertools
from datetime import datetime, timedelta
from urllib import unquote
from urlparse import urlparse, urlunparse
from collections import OrderedDict

from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.http import HttpResponseNotAllowed, HttpResponseServerError, StreamingHttpResponse
from django.core.exceptions import ObjectDoesNotExist
from yabi.yabi.models import User, Credential, BackendCredential
from yabi.yabi.models import ToolGrouping, Tool, ToolDesc, Backend
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from django.core.files.uploadhandler import FileUploadHandler
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from yabi.backend.celerytasks import process_workflow, request_workflow_abort
from yabi.yabiengine.enginemodels import EngineWorkflow
from yabi.yabiengine.models import Workflow, WorkflowTag, SavedWorkflow
from yabi.responses import JsonMessageResponse, JsonMessageResponseBadRequest, JsonMessageResponseForbidden, JsonMessageResponseNotAllowed, JsonMessageResponseNotFound
from yabi.decorators import authentication_required
from yabi.utils import json_error_response, json_response
from yabi.backend import backend
from yabi.backend.exceptions import FileNotFoundError

import logging
logger = logging.getLogger(__name__)

DATE_FORMAT = '%Y-%m-%d'


@authentication_required
def tooldesc(request, tooldesc_id):
    try:
        tool = ToolDesc.objects.get(pk=tooldesc_id)
    except ObjectDoesNotExist:
        return JsonMessageResponseNotFound("Object not found")

    response = HttpResponse(tool.json_pretty(), content_type="application/json; charset=UTF-8")

    return response


@authentication_required
def tool(request, toolid):
    admin_access = False
    if request.GET.get('admin_access', 'false').lower() != 'false':
        admin_access = True

    toolname_key = "%s" % toolid
    page = cache.get(toolname_key)

    if page:
        logger.debug("Returning cached page for tool:%s using key:%s " % (toolid, toolname_key))
        return page

    user = request.user.user
    try:
        tool = Tool.objects.get(pk=toolid)
    except ObjectDoesNotExist:
        return JsonMessageResponseNotFound("Object not found")

    if not (admin_access and request.user.is_superuser):
        if not tool.does_user_have_access_to(user):
            return JsonMessageResponseForbidden("User does not have access to the tool")

    response = HttpResponse(tool.json_pretty(), content_type="application/json; charset=UTF-8")
    cache.set(toolname_key, response, 30)

    return response


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


def menu_all_tools_toolset(django_user):
    all_tools = get_user_tools(django_user.user)

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

    qs = SavedWorkflow.objects.filter(creator__user=user).order_by("created_on")
    qs = qs.select_related("creator")

    toolgroups = [{
        "name": "Saved Workflows",
        "tools": map(make_tool, qs),
    }]

    return {
        "name": "saved_workflows",
        "toolgroups": toolgroups
    }


def get_user_tools(user):
    creds = BackendCredential.objects.filter(credential__user=user)
    backends = list(creds.values_list("backend", flat=True))
    backends.append(Backend.objects.get(name="nullbackend").id)
    user_tools = Tool.objects.filter(enabled=True, backend__in=backends, fs_backend__in=backends)

    qs = ToolGrouping.objects.filter(tool_set__users=user, tool__in=user_tools)
    qs = qs.order_by("tool_group__name", "tool__desc__name")
    qs = qs.select_related("tool_group", "tool", "tool__desc")
    qs = qs.prefetch_related(
        'tool__desc__tooloutputextension_set__file_extension',
        'tool__desc__toolparameter_set__accepted_filetypes__extensions',
        'tool__desc__tool_set',
    )

    all_tools = OrderedDict()
    desc_tool_count = {}
    for toolgroup in qs:
        tg = all_tools.setdefault(toolgroup.tool_group.name, OrderedDict())
        tool = toolgroup.tool
        tg[tool.id] = {
            "name": tool.desc.name,
            "displayName": tool.display_name,
            "defDisplayName": tool.desc.name,
            "description": tool.desc.description,
            "outputExtensions": tool.desc.output_filetype_extensions(),
            "inputExtensions": tool.desc.input_filetype_extensions(),
            "toolId": tool.id,
            "backend": tool.backend.name,
            "descId": tool.desc.id,
            "manyBackends": False
        }
        count = desc_tool_count.get(toolgroup.tool.desc.id, 0)
        desc_tool_count[toolgroup.tool.desc.id] = count + 1

    descsWithManyTools = [k for k, v in desc_tool_count.iteritems() if v > 1]
    for tools in all_tools.values():
        for tool in tools.values():
            if tool['descId'] in descsWithManyTools:
                tool['manyBackends'] = True
            del tool['descId']

    return all_tools


@authentication_required
def ls(request):
    """
    This function will return a list of backends the user has access to IF the uri is empty. If the uri
    is not empty then it will pass on the call to the backend to get a listing of that uri
    """
    yabiusername = request.user.username
    uri = request.GET.get('uri')
    recurse = request.GET.get('recurse')
    logger.debug('yabiusername: {0} uri: {1}'.format(yabiusername, uri))
    if uri:
        listing = backend.get_listing(yabiusername, uri, recurse is not None)
    else:
        listing = backend.get_backend_list(yabiusername)

    return HttpResponse(json.dumps(listing))


@authentication_required
@require_POST
def copy(request):
    """
    This function will instantiate a copy on the backend for this user
    """
    yabiusername = request.user.username

    params = request.GET.copy()  # Support both query params ...
    params.update(request.POST)  # and POST body
    src, dst = params['src'], params['dst']

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
@require_POST
def rcopy(request):
    """
    This function will instantiate a rcopy on the backend for this user
    """
    yabiusername = request.user.username

    params = request.GET.copy()   # Support both query params ...
    params.update(request.POST)   # and POST body
    src, dst = unquote(params['src']), unquote(params['dst'])

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
@require_POST
def rm(request):
    yabiusername = request.user.username

    params = request.GET.copy()   # Support both query params ...
    params.update(request.POST)   # and POST body

    backend.rm_file(yabiusername, params['uri'])
    # TODO Forbidden, any other errors
    return HttpResponse("OK")


@authentication_required
@require_POST
def mkdir(request):
    backend.mkdir(request.user.username, request.GET['uri'])
    return HttpResponse("OK")


def backend_get_file(yabiusername, uri, is_dir=False):
    if is_dir:
        f, thread, status_queue = backend.get_zipped_dir(yabiusername, uri)
    else:
        f, thread, status_queue = backend.get_file(yabiusername, uri)

    CHUNKSIZE = 64 * 1024

    for chunk in iter(lambda: f.read(CHUNKSIZE), ""):
        yield chunk
    f.close()

    success = status_queue.get()

    if not success:
        if thread.exception is not None:
            raise thread.exception
        else:
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
        file_iterator = read_into_iterator(backend_get_file(yabiusername, uri))
        response = StreamingHttpResponse(file_iterator)
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
        file_iterator = read_into_iterator(backend_get_file(yabiusername, uri, is_dir=True))
        response = StreamingHttpResponse(file_iterator)
    except FileNotFoundError:
        response = HttpResponseNotFound()
    else:
        response['content-type'] = "application/x-gtar"
        response['content-disposition'] = 'attachment; filename="%s.tar.gz"' % filename

    return response


# We can't force the Flash uploader to set any headers, so we have to
# disable CSRF for this view.
@csrf_exempt
@authentication_required
@require_POST
def put(request):
    yabiusername = request.user.username
    uri = request.GET['uri']
    upload_handler = DirectBackendUploadHandler(username=yabiusername, uri=uri)
    request.upload_handlers = [upload_handler]

    logger.debug("uri: %s", uri)

    total = len(request.FILES.items())
    succeeded, failed = upload_handler.succeeded, upload_handler.failed

    logger.info("Of a total of %s files to upload, %s succeeded and %s failed.", total, succeeded, failed)

    if failed > 0:
        return HttpResponseServerError("File upload failed")

    response = {
        "level": "success",
        "message": "%s total file(s) uploaded" % total
    }

    return HttpResponse(content=json.dumps(response))


@authentication_required
@transaction.non_atomic_requests
@require_POST
def submit_workflow(request):
    try:
        yabiuser = User.objects.get(name=request.user.username)
        workflow_dict = _preprocess_workflow_json(yabiuser, request.POST["workflowjson"])

        workflow = EngineWorkflow.objects.create(
            name=workflow_dict["name"],
            user=yabiuser,
            shared=workflow_dict.get("shared", False),
            original_json=json.dumps(workflow_dict),
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


def _preprocess_workflow_json(yabiuser, received_json):
    workflow_dict = json.loads(received_json)

    # Check if the user already has a workflow with the same name, and if so,
    # munge the name appropriately.
    workflow_dict["name"] = munge_name(yabiuser.workflow_set, workflow_dict["name"])

    # convert backendName and toolName into toolId
    for job_dict in workflow_dict.get("jobs", []):
        if "toolId" not in job_dict and "backendName" in job_dict:
            tool = Tool.objects.filter(desc__name=job_dict.get("toolName", ""))
            tool = tool.filter(Q(backend__name=job_dict["backendName"]) |
                               Q(backend__name="nullbackend"))[:1]
            if len(tool) > 0:
                job_dict["toolId"] = tool[0].id
                del job_dict["backendName"]

    return workflow_dict


def munge_name(workflow_set, workflow_name):
    if not workflow_set.filter(name=workflow_name).exists():
        return workflow_name

    match = re.search(r"^(.*) \(([0-9]+)\)$", workflow_name)
    base = match.group(1) if match else workflow_name

    workflows = workflow_set.filter(name__startswith=base)
    used_names = frozenset(workflows.values_list("name", flat=True))

    def unused_name(name):
        return name not in used_names

    infinite_range = itertools.count

    generate_unique_names = ("%s (%d)" % (base, i) for i in infinite_range(1))
    next_available_name = find_first(unused_name, generate_unique_names)

    return next_available_name


@authentication_required
@require_POST
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
@require_POST
def delete_workflow(request):
    if "id" not in request.POST:
        return HttpResponseBadRequest("Need id param")

    workflow = get_object_or_404(Workflow, id=request.POST["id"])

    if workflow.user.user != request.user and not request.user.is_superuser:
        return json_error_response("That's not yours", status=403)

    if not workflow.is_finished:
        return json_error_response("Can't delete workflow before it finished running")

    workflow.delete_cascade()

    return json_response("deleted")


@authentication_required
@require_POST
def abort_workflow(request):
    if "id" not in request.POST:
        return HttpResponseBadRequest("Need id param")

    workflow = get_object_or_404(Workflow, id=request.POST["id"])

    if workflow.user.user != request.user and not request.user.is_superuser:
        return json_error_response("That's not yours", status=403)

    if workflow.is_finished:
        return json_error_response("Can't abort workflow after it finished running")

    yabiuser = User.objects.get(name=request.user.username)
    request_workflow_abort(workflow.pk, yabiuser)

    return json_response("abort requested")


@authentication_required
@require_POST
def delete_saved_workflow(request):
    if "id" not in request.POST:
        return HttpResponseBadRequest("Need id param")

    workflow = get_object_or_404(SavedWorkflow, id=request.POST["id"])

    if workflow.creator.user != request.user and not request.user.is_superuser:
        return json_error_response("That's not yours", status=403)

    workflow.delete()

    return json_response("deleted")


@authentication_required
@require_POST
def share_workflow(request):
    if "id" not in request.POST:
        return HttpResponseBadRequest("Need id param")

    workflow = get_object_or_404(Workflow, id=request.POST["id"])

    if workflow.user != request.user.user and not request.user.is_superuser:
        return json_error_response("That's not yours", status=403)

    workflow.share()

    return json_response("shared")


@authentication_required
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
    workflow = workflows[0]

    if not (workflow.user.user == request.user or workflow.shared):
        return json_error_response("The workflow %s isn't yours and the owner '%s' didn't share it with you." % (workflow.id, workflow.user.user), status=403)

    response = workflow_to_response(workflow)

    return HttpResponse(json.dumps(response),
                        content_type='application/json')


def workflow_to_response(workflow, parse_json=True, retrieve_tags=True):
    fmt = DATE_FORMAT
    response = {
        'id': workflow.id,
        'name': workflow.name,
        'last_modified_on': workflow.last_modified_on.strftime(fmt),
        'created_on': workflow.created_on.strftime(fmt),
        'status': workflow.status,
        'is_retrying': workflow.is_retrying,
        'shared': workflow.shared,
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

    def tomorrow():
        return datetime.today() + timedelta(days=1)

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

    return HttpResponse(json.dumps(response), content_type='application/json')


@authentication_required
@require_POST
def workflow_change_tags(request, id=None):
    id = int(id)

    yabiusername = request.user.username
    logger.debug(yabiusername)

    workflow = get_object_or_404(EngineWorkflow, pk=id)
    if workflow.user.user != request.user and not request.user.is_superuser:
        return json_error_response("That's not yours", status=403)

    if 'taglist' not in request.POST:
        return HttpResponseBadRequest("taglist needs to be passed in\n")

    taglist = request.POST['taglist'].split(',')
    taglist = [t.strip() for t in taglist if t.strip()]

    workflow.change_tags(taglist)

    return HttpResponse("Success")


@authentication_required
@require_POST
def passchange(request):

    profile = request.user.user
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

    def exists(value):
        return value is not None and len(value) > 0

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
@require_POST
def save_credential(request, id):
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


def read_into_iterator(target_iterator):
    """Returns the equivalent of target_iterator, but reads the first element
       at call time.
       Use to get errors that would occur only at iteration time at iterator
       creation time."""
    try:
        first_elem = target_iterator.next()
        return itertools.chain(iter((first_elem,)), target_iterator)
    except StopIteration:
        return target_iterator


class DirectBackendUploadHandler(FileUploadHandler):
    """Upload files directly to a Backend with a FIFO without saving it in memory or the FS"""
    def __init__(self, username, uri, *args, **kwargs):
        FileUploadHandler.__init__(self, *args, **kwargs)
        self.username = username
        self.uri = uri
        # Set on each invocation of new_file()
        self.uploader = None
        self.files = {}

    @property
    def succeeded(self):
        return len(filter(lambda x: x is True, self.files.values()))

    @property
    def failed(self):
        return len(filter(lambda x: x is False, self.files.values()))

    def new_file(self, field_name, file_name, content_type, content_length, charset, content_type_extra):
        logger.info('New file %s upload started.', file_name)
        self.uploader = FileToFIFOUploader(self.username, file_name, self.uri)

    def receive_data_chunk(self, raw_data, start):
        return self.uploader.write_chunk(raw_data)

    def file_complete(self, file_size):
        succeeded = self.uploader.upload_complete()
        self.files[self.uploader.file_name] = succeeded
        # Here we should return an UploadedFile instance that will be saved
        # in request.FILES, but at the time request.FILES could be used by the
        # view, we already wrote the file's contents to the destination.
        # To make that clear we return None here.
        return None


class FileToFIFOUploader(object):
    def __init__(self, username, file_name, uri):
        self.username = username
        self.file_name = file_name
        self.uri = uri
        self.upload_handle, self.status_queue = backend.put_file(self.username, self.file_name, self.uri)

    def write_chunk(self, chunk):
        self.upload_handle.write(chunk)
        return None

    def upload_complete(self):
        self.upload_handle.close()
        return self.status_queue.get()
