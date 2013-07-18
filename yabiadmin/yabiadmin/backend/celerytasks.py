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
from functools import wraps
from django.db import transaction
from datetime import datetime
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.backend import backend
from yabiadmin.constants import STATUS_ERROR, STATUS_READY, STATUS_RUNNING, STATUS_COMPLETE, STATUS_EXEC,STATUS_STAGEOUT,STATUS_STAGEIN,STATUS_CLEANING
from yabiadmin.constants import MAX_CELERY_TASK_RETRIES
from yabiadmin.yabiengine.enginemodels import EngineWorkflow, EngineTask
import traceback
from types import LongType, StringType, BooleanType
import celery
from celery import current_task, chain
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


# Celery Tasks working on a Workflow

@celery.task(ignore_result=True)
def build(workflow_id):
    """
    Build a workflow.
    Building a workflow means creating the Job objects in the DB and setting the Workflow's status to READY.
    """ 
    try:
        workflow = EngineWorkflow.objects.get(id=workflow_id)
        workflow.build()
        return workflow.pk

    except Exception, exc:
        logger.exception("Exception in Celery Task build() for workflow {0}".format(workflow_id))
        if workflow.status != STATUS_ERROR:
            workflow.status = STATUS_ERROR
            workflow.save()
        raise


@celery.task(ignore_result=True, max_retries=None)
def walk(workflow_id):
    """
    Walk a workflow
    TODO Make idempotent
    select for update on a walking status
    """
    request = current_task.request
    from yabiadmin.yabi.models import DecryptedCredentialNotAvailable
    try:
         workflow = EngineWorkflow.objects.get(id=workflow_id)
         workflow.walk()
         transaction.commit()
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



def build_workflow(workflow_id):
    chain(build.s(workflow_id) | walk.s() | tasks_to_submit.s()).apply_async()


def walk_workflow(workflow_id):
    chain(walk.s(workflow_id) | tasks_to_submit.s()).apply_async()


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
        workflow = EngineWorkflow.objects.get(id=workflow_id)
        workflow.status = STATUS_ERROR
        workflow.save()
        raise exc
    return workflow_id


@transaction.commit_on_success()
def _task_chain(task_id):
    """Create the task chain for a given task"""
    logger.debug('task chain for {0}'.format(task_id))

    try:
        # Mark the task as requested
        from yabiadmin.yabiengine.models import Task
        updated = Task.objects.filter(pk=task_id, status_requested__isnull=True).update(status_requested=datetime.now())
        if updated == 1:
            chain(stage_in_files.s(task_id) | submit_task.s() | poll_task_status.s() | stage_out_files.s() | clean_up_task.s()).apply_async()
        else:
            logger.warning("Unable to create task chain for {0}".format(task_id))
    except Exception:
        logger.exception("Exception in _task_chain for task {0}".format(task_id))
        raise


# Celery Tasks working on a Yabi Task

def retry_on_error(original_function):
    @wraps(original_function)
    def decorated_function(task_id, *args, **kwargs):
        request = current_task.request
        try:
            return original_function(task_id, *args, **kwargs)
        except RetryException, rexc:
            logger.exception("Exception in celery task submit_task for task {0}".format(task_id))
            countdown = backoff(request.retries)
            try:
                current_task.retry(exc=rexc, countdown=countdown)
                logger.warning('submit_task.retry {0} in {1} seconds'.format(task_id, countdown))
            except RetryException:
                logger.error("submit_task.retry {0} exceeded retry limit - changing status to error".format(task_id))
                change_task_status(task_id, STATUS_ERROR)
                raise
            except celery.exceptions.RetryTaskError:
                raise
            except Exception, ex:
                logger.error(("submit_task.retry {0} failed: {1} - changing status to error".format(task_id, ex)))
                change_task_status(task_id, STATUS_ERROR)
                raise

    return decorated_function



@celery.task(ignore_result=True, max_retries=None)
@retry_on_error
def stage_in_files(task_id):
    task = EngineTask.objects.get(pk=task_id)
    change_task_status(task.pk, STATUS_STAGEIN)
    backend.stage_in_files(task)
    return task_id


@celery.task(ignore_result=True, max_retries=MAX_CELERY_TASK_RETRIES)
@retry_on_error
def submit_task(task_id):
    task = EngineTask.objects.get(pk=task_id)
    backend.submit_task(task)
    change_task_status(task.pk, STATUS_EXEC)
    return task_id


@celery.task(ignore_result=True, max_retries=None)
@retry_on_error
def poll_task_status(task_id):
    task = EngineTask.objects.get(pk=task_id)
    backend.poll_task_status(task)
    return task_id


@celery.task(ignore_result=True, max_retries=None)
@retry_on_error
def stage_out_files(task_id):
    task = EngineTask.objects.get(pk=task_id)
    change_task_status(task.pk, STATUS_STAGEOUT)
    backend.stage_out_files(task)
    return task_id


@celery.task(ignore_result=True, max_retries=None)
@retry_on_error
def clean_up_task(task_id):
    task = EngineTask.objects.get(pk=task_id)
    change_task_status(task.pk, STATUS_CLEANING)
    backend.clean_up_task(task)
    change_task_status(task.pk, STATUS_COMPLETE)



# Implementation

def backoff(count=0):
    """
    Provide an exponential backoff with a maximum backoff in seconds
    Used to delay between task retries
    """
    if count > 4:
        count = 4
    return 5 ** (count + 1)



# Service methods 
# TODO TSZ move to another file?

@transaction.commit_manually()
def change_task_status(task_id, status):
    try:
        task = EngineTask.objects.get(pk=task_id)
        logger.debug("Setting status of task {0} to {1}".format(task_id, status))
        task.set_status(status)
        task.save()
        job_status_changed = task.cascade_status()

        if job_status_changed:
            # commit before submission of Celery Tasks
            transaction.commit()
            rewalk_workflow_if_needed(task)

        transaction.commit()

    except Exception:
        transaction.rollback()
        logger.exception("Exception when updating task's {0} status to {1}".format(task_id, status))
        raise

def rewalk_workflow_if_needed(task):
    if task.job.status in [STATUS_READY, STATUS_COMPLETE, STATUS_ERROR]:
        workflow = EngineWorkflow.objects.get(pk=task.job.workflow.pk)
        if workflow.needs_walking():
            walk_workflow(workflow_id=workflow.pk)
 


