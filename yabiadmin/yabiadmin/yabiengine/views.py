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
from datetime import datetime
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core import urlresolvers
from django.db import transaction 
from django.utils import simplejson as json
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from ccg.utils import webhelpers
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog
from yabiadmin.yabiengine.enginemodels import EngineTask, EngineJob, EngineWorkflow
from yabiadmin.yabi.models import BackendCredential
from yabiadmin.decorators import authentication_required, hmac_authenticated


import logging
logger = logging.getLogger(__name__)

from yabiadmin.constants import *
from random import shuffle


@hmac_authenticated
def status(request, model, id):
    models = {'task':EngineTask, 'job':EngineJob, 'workflow':EngineWorkflow}

    # sanity checks
    if model.lower() not in models.keys():
        raise ObjectDoesNotExist()

    if request.method == 'GET':
        try:
            m = models[model.lower()]
            obj = m.objects.get(id=id)
            return HttpResponse(json.dumps({'status':obj.status}))
        except ObjectDoesNotExist, e:
            return HttpResponseNotFound('Object not found')
    elif request.method == 'POST':
        if 'status' not in request.POST:
            return HttpResponseServerError('POST request to status service should contain status parameter\n')

        try:
            model = str(model).lower()
            id = int(id)
            status = str(request.POST['status'])

            if model != 'task':
                return HttpResponseServerError('Only the status of Tasks is allowed to be changed\n')

            logger.debug('task id: %s status=%s' % (id, request.POST['status']))

            # TODO TSZ maybe raise exception instead?
            # truncate status to 64 chars to avoid any sql field length errors
            status = status[:64]
            task = EngineTask.objects.get(pk=id)
        except (ObjectDoesNotExist,ValueError):
            return HttpResponseNotFound('Task not found')

        try:
            _update_task_status(task.pk, status)
        except Exception, e:
            return HttpResponseServerError(e)

        return HttpResponse('OK')


@hmac_authenticated
def remote_id(request,id):
    logger.debug('remote_task_id> %s' % id)
    try:
        if 'remote_id' not in request.POST:
            return HttpResponseServerError('POST request to remote_id service should contain remote_id parameter\n')

        id = int(id)
        remote_id = str(request.POST['remote_id'])

        logger.debug('remote_id='+request.POST['remote_id'])

        # truncate status to 256 chars to avoid any sql field length errors
        remote_id = remote_id[:256]

        obj = EngineTask.objects.get(id=id)
        obj.remote_id = remote_id
        obj.save()

        return HttpResponse('')
    except (ObjectDoesNotExist,ValueError):
        return HttpResponseNotFound('Task not found')
    except Exception, e:
        import traceback
        logger.critical(traceback.format_exc())
        logger.critical('Caught Exception: %s' % e)
        return HttpResponseServerError(e)


@hmac_authenticated
def remote_info(request,id):
    logger.debug('remote_task_info> %s' % id)
    try:
        if 'remote_info' not in request.POST:
            return HttpResponseServerError('POST request to remote_info service should contain remote_info parameter\n')

        id = int(id)
        remote_info = str(request.POST['remote_info'])

        logger.debug('remote_info=' + request.POST['remote_info'])

        # truncate status to 2048 chars to avoid any sql field length errors
        remote_info = remote_info[:2048]

        obj = EngineTask.objects.get(id=id)
        obj.remote_info = remote_info
        obj.save()

        return HttpResponse('')
    except (ObjectDoesNotExist,ValueError):
        return HttpResponseNotFound('Object not found')
    except Exception, e:
        import traceback
        logger.critical(traceback.format_exc())
        logger.critical('Caught Exception: %s' % e)
        return HttpResponseServerError(e)


@hmac_authenticated
def syslog(request, table, id):
    try:
        if request.method == 'GET':
            entries = Syslog.objects.filter(table_name=table, table_id=id)

            if not entries:
                raise ObjectDoesNotExist()

            output = [{'table_name':x.table_name, 'table_id':x.table_id, 'message':x.message} for x in entries]
            return HttpResponse(json.dumps(output))

        else:
            # check we have required params
            if 'message' not in request.POST:
                return HttpResponseServerError('POST request to syslog service should contain message parameter\n')

            logger.debug('table: %s id: %s message: %s' % (table, id, request.POST['message']))
            syslog = Syslog(table_name=str(table), table_id=int(id), message=str(request.POST['message']))
            syslog.save()

            return HttpResponse('OK')

    except ObjectDoesNotExist, o:
        logger.critical('Caught Exception: %s' % o.message)
        return HttpResponseNotFound('Object not found')
    except ValueError, ve:
        logger.critical('Caught Exception: %s' % ve.message)
        return HttpResponseNotFound('Object not found')
    except Exception, e:
        logger.critical('Caught Exception: %s' % e.message)
        return HttpResponseNotFound('Object not found')


@hmac_authenticated
def job(request, workflow, order):
    try:
        workflow = EngineWorkflow.objects.get(id=int(workflow))
        job = EngineJob.objects.get(workflow=workflow, order=int(order))

        # Put some fields of general interest in.
        output = {
            'id': job.id,
            'status': job.status,
            'tasks': [],
        }

        for task in job.task_set.all():
            try:
                remote_info = json.loads(task.remote_info)
            except (TypeError, ValueError):
                # JSON failed to decode or was null.
                remote_info = None

            output['tasks'].append({
                'id': task.id,
                'percent_complete': task.percent_complete,
                'remote_id': task.remote_id,
                'remote_info': remote_info,
            })

        return HttpResponse(json.dumps(output), mimetype='application/json')
    except (MultipleObjectsReturned, ObjectDoesNotExist, ValueError):
        return HttpResponseNotFound('Object not found')
    except Exception, e:
        logger.critical('Caught Exception: %s' % e.message)
        return HttpResponseNotFound('Object not found')


@staff_member_required
def task_json(request, task):
    logger.debug('task_json> %s' % task)

    try:
        task = Task.objects.get(id=int(task))
        return HttpResponse(content=task.json(), content_type='application/json; charset=UTF-8')
    except (ObjectDoesNotExist, ValueError):
        return HttpResponseNotFound('Task not found')


@staff_member_required
def workflow_summary(request, workflow_id):
    logger.debug('')

    workflow = get_object_or_404(EngineWorkflow, pk=workflow_id)
   
    return render_to_response('yabiengine/workflow_summary.html', {
        'w': workflow,
        'user': request.user,
        'title': 'Workflow Summary',
        'root_path': urlresolvers.reverse('admin:index'),
        'settings': settings
        })
