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
from yabiadmin.yabiengine.tasks import walk
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog
from yabiadmin.yabiengine.enginemodels import EngineTask, EngineJob, EngineWorkflow
from yabiadmin.yabi.models import BackendCredential
from yabiadmin.decorators import authentication_required, hmac_authenticated


import logging
logger = logging.getLogger(__name__)

from yabiadmin.constants import *
from random import shuffle


def request_next_task(request, status):
    # check tasktag
    if 'tasktag' not in request.REQUEST or request.REQUEST['tasktag'] != settings.TASKTAG:
        logger.critical('Expected tasktag %s got %s.' % (settings.TASKTAG, tasktag))
        return HttpResponseServerError('Error requesting task. Tasktag incorrect.')
    tasktag = request.REQUEST['tasktag']

    # tasks waiting execution, fifo, for given status
    ready_tasks = []
    if status == STATUS_READY:
        ready_tasks = Task.objects.filter(tasktag=tasktag).filter(status_requested__isnull=True, status_ready__isnull=False).order_by('id')
    elif status == STATUS_RESUME:
        # not implemented, there is no resume status
        return HttpResponseNotFound('No more tasks.')
    else:
        return HttpResponseServerError('Unknown status for next task')

    if len(ready_tasks) == 0:
        logger.debug('No more tasks.')
        return HttpResponseNotFound('No more tasks.')

    # find a task to make available
    throttled = []
    for task in ready_tasks:
        # if the backend credential for this task has already been throttled, skip task
        if task.execution_backend_credential.id in throttled:
            logger.debug('backend credential already throttled')
            continue

        # determine active tasks for the execution backend credential associated with this task
        tasks_active_per_bec = Task.objects.filter(execution_backend_credential=task.execution_backend_credential).filter(tasktag=tasktag).exclude(status_requested__isnull=True).exclude(status_complete__isnull=False).exclude(job__workflow__status=STATUS_ERROR).exclude(job__workflow__status=STATUS_EXEC_ERROR).exclude(job__workflow__status=STATUS_COMPLETE)
        tasks_per_user = task.execution_backend_credential.backend.tasks_per_user
        active_tasks = len(tasks_active_per_bec)

        # skip tasks if too many tasks active for this backend cred 
        if tasks_per_user is not None and active_tasks >= tasks_per_user:
            logger.warn("Throttling {0} {1}>={2}".format(task.execution_backend_credential,active_tasks, tasks_per_user))
            throttled.append(task.execution_backend_credential.id)
            continue

        # make sure the task we are about to make available is ours for the taking
        updated = Task.objects.filter(id=task.id, status_requested__isnull=True).update(status_requested=datetime.now())
        if updated == 1:
            logger.info('next %s task id: %s command: %s' % (status, task.id, task.command))
            return HttpResponse(task.json())

    logger.debug('No more tasks.')
    return HttpResponseNotFound('No more tasks.')


def old_request_next_task(request, status):
    if 'tasktag' not in request.REQUEST:
        return HttpResponseServerError('Error requesting task. No tasktag identifier set.')
    
    # verify that the requesters tasktag is correct
    tasktag = request.REQUEST['tasktag']
    if tasktag != settings.TASKTAG:
        logger.critical('Task requested  had incorrect identifier set. Expected tasktag %s but got %s instead.' % (settings.TASKTAG, tasktag))
        return HttpResponseServerError('Error requesting task. Tasktag incorrect. This is not the admin you are looking for.')
    
    # we assemble a list of backendcredentials. This way we can rate control the jobs a particular backend user and backend sees to
    # prevent overload of the scheduler, which is what a job scheduler should deal with, with something like, you know, a queue. but most of them
    # don't. cause they're mostly rubbish.
    backend_user_pairs = [bec for bec in BackendCredential.objects.all()]
    
    # we shuffle this list to try to prevent any starvation of later backend/user pairs
    shuffle(backend_user_pairs)
    
    # for each backend/user pair, we count how many submitted jobs there are. Those with no bec setting are always done first.
    # this enables us later to allow a backend task to be submitted no matter what the remote backend is doing, simply by leaving the column null
    for bec in [None] + backend_user_pairs:
        # the following collects the list of tasks for this bec that are already running on the remote
        #logger.warning('bec: %s tasktag: %s'%(str(bec),str(tasktag)))
        remote_task_candidates = Task.objects.filter(execution_backend_credential=bec).filter(tasktag=tasktag).exclude(job__workflow__status=STATUS_ERROR).exclude(job__workflow__status=STATUS_EXEC_ERROR).exclude(job__workflow__status=STATUS_COMPLETE)
        #logger.warning('candidates: %s'%(str(remote_task_candidates)))
        
        remote_tasks = []
        for n,t in enumerate(remote_task_candidates):
            s = t.status
            #logger.warning('status for %d is: %s'%(n,status))
            if s not in [STATUS_READY, STATUS_ERROR, STATUS_EXEC_ERROR, STATUS_COMPLETE]:
                remote_tasks.append(t)
        
        #logger.warning('remote_tasks: %s'%(str(remote_tasks)))
        
        tasks_per_user = None if not bec or bec.backend.tasks_per_user==None else bec.backend.tasks_per_user
        
        #logger.debug('%d remote tasks running for this bec (%s)'%(len(remote_tasks),bec))
        #logger.debug('tasks_per_user = %s\n'%(tasks_per_user))
        
        if tasks_per_user==None or len(remote_tasks) < tasks_per_user:
            # we can return a task for this bec if one exists
            try:
                tasks = [T for T in Task.objects.filter(execution_backend_credential=bec).filter(tasktag=tasktag).filter(status_requested__isnull=True) if T.status==status]
                
                #logger.warning('FOUND %s: (%d tasks) %s'%(status,len(tasks),tasks))
                
                # Optimistic locking
                # Update and return task only if another thread hasn't updated and returned it before us
                for task in tasks:
                    updated = Task.objects.filter(id=task.id, status_requested__isnull=True).update(status_requested=datetime.now())
                    if updated == 1:
                        logger.debug('requested %s task id: %s command: %s' % (status, task.id, task.command))
                        return HttpResponse(task.json())

            except ObjectDoesNotExist:
                # this bec has no jobs... continue to try the next one...
                #logger.warning('ODNE')
                pass
            
    logger.debug('No more tasks.')
    return HttpResponseNotFound('No more tasks.')


@hmac_authenticated
def task(request):
    return request_next_task(request, status=STATUS_READY)


@hmac_authenticated
def blockedtask(request):
    return request_next_task(request, status=STATUS_RESUME)


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


@transaction.commit_manually
def _update_task_status(task_id, status):
    try:
        kwargs = {Task.status_attr(status): datetime.now()}
        Task.objects.filter(id=task_id).update(**kwargs)
        task = Task.objects.get(id=task_id)

        if status != STATUS_BLOCKED and status!= STATUS_RESUME:
            task.percent_complete = STATUS_PROGRESS_MAP[status]

        if status == STATUS_COMPLETE:
            task.end_time = datetime.now()
       
        # We have to commit the task status before calculating
        # job status that is based on task statuses
        task.save()
        transaction.commit()
 
        # update the job status when the task status changes
        job_old_status = task.job.status
        job_cur_status = task.job.update_status()
        transaction.commit()

        if job_cur_status != job_old_status and job_cur_status in (STATUS_ERROR, STATUS_COMPLETE):
            task.job.workflow.update_status()
            transaction.commit()
        
        if job_cur_status in [STATUS_READY, STATUS_COMPLETE, STATUS_ERROR]:
            workflow = EngineWorkflow.objects.get(pk=task.job.workflow.id)
            if workflow.needs_walking():
                # trigger a walk via celery 
                walk.delay(workflow_id=workflow.pk)
        transaction.commit()
    except Exception, e:
        transaction.rollback()
        import traceback
        logger.critical(traceback.format_exc())
        logger.critical('Caught Exception: %s' % e)
        raise


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
