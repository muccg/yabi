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
from django.db import transaction
from datetime import datetime
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.backend import backend 
from yabiadmin.constants import STATUS_ERROR, STATUS_READY, STATUS_RUNNING, STATUS_COMPLETE
import traceback
from types import LongType, StringType, BooleanType
import celery
from celery import current_task, chain
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


#@transaction.commit_manually
@transaction.commit_on_success()
def _task_chain(task_id):
    """Create the task chain for a given task"""
    assert type(task_id) is LongType, '{0} not a long'.format(type(task_id))
    logger.debug('task chain for {0}'.format(task_id))

    try:
        # Mark the task as requested
        from yabiadmin.yabiengine.models import Task
        updated = Task.objects.filter(id=task_id, status_requested__isnull=True).update(status_requested=datetime.now())
        if updated == 1:
            chain(stage_in_files.s(task_id) | submit_task.s() | poll_task_status.s() | stage_out_files.s() | clean_up_task.s()).apply_async()
        else:
            logger.warning('Unable to create task chain for {0} update returned {1}'.format(task_id, updated))
    except Exception:
        logger.error(traceback.format_exc())
        raise


def backoff(count=0):
    """
    Provide an exponential backoff with a maximum backoff in seconds
    Typically used to delay between task retries
    """
    if count > 4:
        count = 4
    return 5 ** (count + 1)


@transaction.commit_on_success()
def build_workflow(workflow_id):
    """
    Build a workflow, walk it, then submit tasks
    We don't know how the upstream django code block will handle transactions,
    so within this block handle transactions manually to avoid side effects
    """
    assert type(workflow_id) is LongType, '{0} not a long'.format(type(workflow_id))
    try:
        chain(build.s(workflow_id) | walk.s() | tasks_to_submit.s()).apply_async()
    except Exception:
        logger.error(traceback.format_exc())
        raise


@transaction.commit_on_success()
def walk_workflow(workflow_id):
    """
    Walk a workflow then submit tasks
    We don't know how the upstream django code block will handle transactions,
    so within this block handle transactions manually to avoid side effects
    """
    assert type(workflow_id) is LongType, '{0} not a long'.format(type(workflow_id))
    try:
        chain(walk.s(workflow_id) | tasks_to_submit.s()).apply_async()
    except Exception:
        logger.error(traceback.format_exc())
        raise


@transaction.commit_on_success()
def _stage_in_files(task_id):
    from yabiadmin.yabiengine.enginemodels import EngineTask
    task = EngineTask.objects.get(id=task_id)
    backend.stage_in_files(task)


@celery.task(ignore_result=True, max_retries=None)
def stage_in_files(task_id):
    """Stage in files for a given task"""
    assert type(task_id) is LongType, '{0} not a long'.format(type(task_id))
    request = current_task.request
    try:
        _stage_in_files(task_id)
    except RetryException, rexc:
        logger.error(traceback.format_exc())
        logger.error(rexc)
        countdown = backoff(request.retries)
        logger.warning('stage_in_files.retry {0} in {1} seconds'.format(task_id, countdown))
        raise stage_in_files.retry(exc=rexc, countdown=countdown)
    return task_id


@transaction.commit_on_success()
def _submit_task(task_id):
    from yabiadmin.yabiengine.enginemodels import EngineTask
    task = EngineTask.objects.get(id=task_id)
    backend.submit_task(task)
    _task_status(task, 'exec:running')


@celery.task(ignore_result=True, max_retries=None)
def submit_task(task_id):
    """Submit a task"""
    assert type(task_id) is LongType, '{0} not a long'.format(type(task_id))
    request = current_task.request
    try:
        _submit_task(task_id)
    except RetryException, rexc:
        logger.error(traceback.format_exc())
        logger.error(rexc)
        countdown = backoff(request.retries)
        logger.warning('submit_task.retry {0} in {1} seconds'.format(task_id, countdown))
        raise submit_task.retry(exc=rexc, countdown=countdown)
    return task_id


@celery.task(ignore_result=True, max_retries=None)
def poll_task_status(task_id):
    """
    Poll the status of a task. 
    Will retry with backoff until complete.
    """
    assert type(task_id) is LongType, '{0} not a long'.format(type(task_id))
    request = current_task.request
    try:
        from yabiadmin.yabiengine.enginemodels import EngineTask
        task = EngineTask.objects.get(id=task_id)
        backend.poll_task_status(task)
    except RetryException, rexc:
        logger.error(traceback.format_exc())
        logger.error(rexc)
        countdown = backoff(request.retries)
        logger.debug('poll_task_status.retry {0} in {1} seconds'.format(task_id, countdown))
        raise poll_task_status.retry(exc=rexc, countdown=countdown)
    return task_id


@transaction.commit_on_success()
def _stage_out_files(task_id):
    from yabiadmin.yabiengine.enginemodels import EngineTask
    task = EngineTask.objects.get(id=task_id)
    backend.stage_out_files(task)


@celery.task(ignore_result=True, max_retries=None)
def stage_out_files(task_id):
    """Stage out files for a given task"""
    assert type(task_id) is LongType, '{0} not a long'.format(type(task_id))
    request = current_task.request
    try:
        _stage_out_files(task_id)
    except RetryException, rexc:
        logger.error(traceback.format_exc())
        logger.error(rexc)
        countdown = backoff(request.retries)
        logger.warning('stage_out_files.retry {0} in {1} seconds'.format(task_id, countdown))
        raise stage_out_files.retry(exc=rexc, countdown=countdown)
    return task_id


@transaction.commit_manually()
def _task_status(task, status):
    logger.debug('_task_status {0} {1}'.format(task, status))
    try:
        task.set_status(status)
        task.save()
        transaction.commit()
        task.cascade_status()
        transaction.commit()
    except Exception:
        transaction.rollback()
        logger.error(traceback.format_exc())
        raise


@transaction.commit_manually()
def _clean_up_task(task_id):
    logger.debug('_clean_up_task {0}'.format(task_id))
    try:
        from yabiadmin.yabiengine.enginemodels import EngineTask
        task = EngineTask.objects.get(id=task_id)
        backend.clean_up_task(task)
        transaction.commit()
        _task_status(task, STATUS_COMPLETE)
        transaction.commit()
    except Exception:
        logger.error(traceback.format_exc())
        transaction.rollback()
        raise


@celery.task(ignore_result=True, max_retries=None)
def clean_up_task(task_id):
    """Clean up after a task"""
    assert type(task_id) is LongType, '{0} not a long'.format(type(task_id))
    request = current_task.request
    try:
        _clean_up_task(task_id)
    except RetryException, rexc:
        logger.error(traceback.format_exc())
        logger.error(rexc)
        countdown = backoff(request.retries)
        logger.warning('clean_up_task.retry {0} in {1} seconds'.format(task_id, countdown))
        raise clean_up_task.retry(exc=rexc, countdown=countdown)
    return task_id


@celery.task(ignore_result=True)
def tasks_to_submit(workflow_id):
    """Determine what tasks are able to be submitted for a workflow"""
    assert type(workflow_id) is LongType, '{0} not a long'.format(type(workflow_id))
    logger.debug('tasks_to_submit for workflow {0}'.format(workflow_id))
    request = current_task.request
    try:
        from yabiadmin.yabiengine.models import Task
        # TODO deprecate tasktag
        #ready_tasks = Task.objects.filter(tasktag=tasktag).filter(status_requested__isnull=True, status_ready__isnull=False).order_by('id')
        tasks = Task.objects.filter(job__workflow__id=workflow_id).order_by('id')
        logger.debug(tasks)
        for task in tasks:
            logger.debug(task)

        ready_tasks = Task.objects.filter(job__workflow__id=workflow_id).filter(status_requested__isnull=True, status_ready__isnull=False).order_by('id')
        logger.debug(ready_tasks)
        for task in ready_tasks:
            _task_chain(task.id)
    except Exception, exc:
        logger.error(traceback.format_exc())
        logger.error(exc)
        from yabiadmin.yabiengine.enginemodels import EngineWorkflow
        workflow = EngineWorkflow.objects.get(id=workflow_id)
        workflow.status = STATUS_ERROR
        workflow.save()
        raise exc
    return workflow_id


@transaction.commit_manually()
def _build(workflow_id):
    from yabiadmin.yabiengine.enginemodels import EngineWorkflow
    workflow = EngineWorkflow.objects.get(id=workflow_id)
    workflow.build()
    transaction.commit()
    return workflow


@celery.task(ignore_result=True)
def build(workflow_id):
    """
    Build a workflow
    TODO Make idempotent
    select for update on a build status
    """ 
    assert type(workflow_id) is LongType, '{0} not a long'.format(type(workflow_id))
    request = current_task.request
    try:
        workflow = _build(workflow_id)
    except Exception, exc:
        logger.error(traceback.format_exc())
        logger.error(exc)
        try:
            workflow.status = STATUS_ERROR
            workflow.save()
        except Exception:
            logger.error(traceback.format_exc())
            pass
        raise exc
    return workflow_id


@transaction.commit_manually()
def _walk(workflow_id):
    from yabiadmin.yabiengine.enginemodels import EngineWorkflow
    workflow = EngineWorkflow.objects.get(id=workflow_id)
    workflow.walk()
    transaction.commit()


@celery.task(ignore_result=True, max_retries=None)
def walk(workflow_id):
    """
    Walk a workflow
    TODO Make idempotent
    select for update on a walking status
    """
    assert type(workflow_id) is LongType, '{0} not a long'.format(type(workflow_id))
    request = current_task.request
    from yabiadmin.yabi.models import DecryptedCredentialNotAvailable
    try:
        _walk(workflow_id)
    except DecryptedCredentialNotAvailable, dcna:
        logger.error("Decrypted credential not available.")
        logger.error(dcna)
        countdown = backoff(request.retries)
        logger.warning('walk.retry {0} in {1} seconds'.format(workflow_id, countdown))
        raise walk.retry(exc=dcna, countdown=countdown)
    except Exception, exc:
        logger.error(traceback.format_exc())
        logger.error(exc)
        try:
            workflow.status = STATUS_ERROR
            workflow.save()
        except Exception:
            logger.error(traceback.format_exc())
            pass
        raise exc
    return workflow_id
