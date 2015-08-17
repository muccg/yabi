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

import json
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.core import urlresolvers
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from yabi.yabiengine.models import Task
from yabi.yabiengine.enginemodels import EngineWorkflow
from yabi.constants import *
import logging
logger = logging.getLogger(__name__)


@staff_member_required
def task_json(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.user != task.user.user and not request.user.is_superuser:
        return HttpResponseForbidden("That's not yours")

    return HttpResponse(content=task.json(), content_type='application/json; charset=UTF-8')


@staff_member_required
def workflow_summary(request, workflow_id):
    logger.debug('')

    workflow = get_object_or_404(EngineWorkflow, pk=workflow_id)
    if request.user != workflow.user.user and not request.user.is_superuser:
        return HttpResponseForbidden("That's not yours")

    jobs_by_order = workflow.job_set.all().order_by('order')
    if workflow.json:
        workflow_json = json.dumps(json.loads(workflow.json), indent=2)
    else:
        workflow_json = None

    return render_to_response('yabiengine/workflow_summary.html', {
        'w': workflow,
        'workflow_json': workflow_json,
        'jobs_by_order': jobs_by_order,
        'user': request.user,
        'title': 'Workflow Summary',
        'root_path': urlresolvers.reverse('admin:index'),
        'settings': settings
    })
