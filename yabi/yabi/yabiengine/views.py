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
# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
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
    return HttpResponse(content=task.json(), content_type='application/json; charset=UTF-8')


@staff_member_required
def workflow_summary(request, workflow_id):
    logger.debug('')

    workflow = get_object_or_404(EngineWorkflow, pk=workflow_id)

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
