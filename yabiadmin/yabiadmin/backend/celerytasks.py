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
from yabiadmin.yabi.models import DecryptedCredentialNotAvailable
from yabiadmin.yabiengine.models import Task
from yabiadmin.yabiengine.enginemodels import EngineWorkflow, EngineJob, EngineTask
import celery
from celery import current_task, chain
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


# Celery Tasks working on a Workflow

def process_workflow(workflow_id):
    return chain(create_jobs.s(workflow_id) | process_jobs.s())


@celery.task
def create_jobs(workflow_id):
    workflow = EngineWorkflow.objects.get(pk=workflow_id)
    workflow.create_jobs()
    return workflow.pk


@celery.task
def process_jobs(workflow_id):
    workflow = EngineWorkflow.objects.get(pk=workflow_id)
    for job in workflow.jobs_that_need_processing():
        chain(create_db_tasks.s(job.pk) | spawn_ready_tasks.s()).apply_async()


# Celery Tasks working on a Job


@celery.task(max_retries=None)
def create_db_tasks(job_id):
    request = current_task.request
    try:
        job = EngineJob.objects.get(pk=job_id)
        tasks_count = job.create_tasks()
        if not tasks_count:
            return None
        return job_id
    except DecryptedCredentialNotAvailable, dcna:
        logger.exception("Decrypted credential not available.")
        countdown = backoff(request.retries)
        logger.warning('create_db_tasks.retry {0} in {1} seconds'.format(job_id, countdown))
        raise current_task.retry(exc=dcna, countdown=countdown)
    except Exception, exc:
        logger.exception("Exception in create_db_tasks for job {0}".format(job_id))
        job.status = STATUS_ERROR
        job.workflow.status = STATUS_ERROR
        job.save()
        job.workflow.save()
        raise


@celery.task()
def spawn_ready_tasks(job_id):
    logger.debug('spawn_ready_tasks for job {0}'.format(job_id))
    if job_id is None:
        logger.debug('no tasks to process, exiting early')
        return
    request = current_task.request
    try:
        # TODO deprecate tasktag
        job = EngineJob.objects.get(pk=job_id)
        ready_tasks = job.ready_tasks()
        logger.debug(ready_tasks)
        for task in ready_tasks:
            spawn_task(task.pk)
            # need to update task.job.status here when all tasks for job spawned ?

        return job_id

    except Exception, exc:
        logger.exception("Exception when submitting tasks for job {0}".format(job_id))
        job = EngineJob.objects.get(pk=job_id)
        job.status = STATUS_ERROR
        job.workflow.status = STATUS_ERROR
        job.save()
        job.workflow.save()
        raise


# Celery Tasks working on a Yabi Task

@transaction.commit_on_success()
def spawn_task(task_id):
    logger.debug('Spawn task {0}'.format(task_id))

    task = Task.objects.get(pk=task_id)
    task.set_status('requested')
    task.save()
    transaction.commit()
    chain(stage_in_files.s(task_id) | submit_task.s() | poll_task_status.s() | stage_out_files.s() | clean_up_task.s()).apply_async()


def retry_on_error(original_function):
    @wraps(original_function)
    def decorated_function(task_id, *args, **kwargs):
        request = current_task.request
        original_function_name = original_function.__name__
        try:
            result = original_function(task_id, *args, **kwargs)
            return result
        except RetryException, rexc:
            logger.exception("Exception in celery task submit_task for task {0}".format(task_id))
            countdown = backoff(request.retries)
            try:
                current_task.retry(exc=rexc, countdown=countdown)
                logger.warning('{0}.retry {1} in {2} seconds'.format(original_function_name,task_id, countdown))
            except RetryException:
                logger.error("{0}.retry {1} exceeded retry limit - changing status to error".format(original_function_name, task_id))
                change_task_status(task_id, STATUS_ERROR)
                raise
            except celery.exceptions.RetryTaskError:
                raise
            except Exception, ex:
                logger.error(("{0}.retry {1} failed: {2} - changing status to error".format(original_function_name, task_id, ex)))
                change_task_status(task_id, STATUS_ERROR)
                raise

    return decorated_function



@celery.task(max_retries=None)
@retry_on_error
def stage_in_files(task_id):
    task = EngineTask.objects.get(pk=task_id)
    change_task_status(task.pk, STATUS_STAGEIN)
    backend.stage_in_files(task)
    return task_id


@celery.task(max_retries=MAX_CELERY_TASK_RETRIES)
@retry_on_error
def submit_task(task_id):
    task = EngineTask.objects.get(pk=task_id)
    backend.submit_task(task)
    change_task_status(task.pk, STATUS_EXEC)
    return task_id


@celery.task(max_retries=None)
@retry_on_error
def poll_task_status(task_id):
    task = EngineTask.objects.get(pk=task_id)
    backend.poll_task_status(task)
    return task_id


@celery.task(max_retries=None)
@retry_on_error
def stage_out_files(task_id):
    task = EngineTask.objects.get(pk=task_id)
    change_task_status(task.pk, STATUS_STAGEOUT)
    backend.stage_out_files(task)
    return task_id


@celery.task(max_retries=None)
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
        logger.debug("Setting status of task {0} to {1}".format(task_id, status))
        task = EngineTask.objects.get(pk=task_id)
        task.set_status(status)
        task.save()
        job_status_changed = task.cascade_status()

        if job_status_changed:
            # commit before submission of Celery Tasks
            transaction.commit()
            process_workflow_jobs_if_needed(task)

        transaction.commit()

    except Exception:
        transaction.rollback()
        logger.exception("Exception when updating task's {0} status to {1}".format(task_id, status))
        raise

def process_workflow_jobs_if_needed(task):
    if task.job.status == STATUS_COMPLETE:
        workflow = EngineWorkflow.objects.get(pk=task.job.workflow.pk)
        if workflow.has_jobs_to_process():
            process_jobs.apply_async((workflow.pk,))
 


