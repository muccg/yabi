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
from __future__ import absolute_import
from functools import partial, wraps
from django.db import transaction
from datetime import datetime
from celery import chain
from celery.utils.log import get_task_logger
from six.moves import filter
from yabiadmin.backend.exceptions import RetryPollingException, JobNotFoundException
from yabiadmin.backend import backend
from yabiadmin.constants import STATUS_ERROR, STATUS_READY, STATUS_COMPLETE, STATUS_EXEC, STATUS_STAGEOUT, STATUS_STAGEIN, STATUS_CLEANING, STATUS_ABORTED
from yabiadmin.constants import MAX_CELERY_TASK_RETRIES
from yabiadmin.yabi.models import DecryptedCredentialNotAvailable
from yabiadmin.yabiengine.models import Job, Task, Syslog
from yabiadmin.yabiengine.enginemodels import EngineWorkflow, EngineJob, EngineTask
from yabiadmin.yabiengine.engine_logging import create_workflow_logger, create_job_logger, create_task_logger, create_logger, YabiDBHandler, YabiContextFilter
from yabiadmin.backend import provisioning
import celery
from django.conf import settings
from django.db.models import Q
from celery.signals import after_setup_task_logger
import logging

logger = get_task_logger(__name__)

app = celery.Celery('yabiadmin.backend.celerytasks')

app.config_from_object('django.conf:settings')

DYNBE_READY_POLL_INTERVAL = getattr(settings, 'DYNBE_READY_POLL_INTERVAL', 60)
TASK_LIMIT_REACHED_RETRY_INTERVAL = getattr(settings, 'TASK_LIMIT_REACHED_RETRY_INTERVAL', 10)


# Celery uses its own logging setup. All our custom logging setup has to be
# done in this callback
def setup_logging(*args, **kwargs):
    handler = YabiDBHandler()
    log_filter = YabiContextFilter()
    handler.addFilter(log_filter)
    level = getattr(settings, 'YABIDBHANDLER_LOG_LEVEL', 'DEBUG')
    handler.setLevel(logging.getLevelName(level))
    logger.addHandler(handler)

    yabiadminLogger = logging.getLogger('yabiadmin')
    yabiadminLogger.propagate = 1

    syslog_formatter = logging.Formatter('YABI [%(name)s:%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s')
    syslog_handler = logging.handlers.SysLogHandler(address='/dev/log', facility='local4')
    syslog_handler.setLevel('DEBUG')
    syslog_handler.setFormatter(syslog_formatter)
    logger.addHandler(syslog_handler)

after_setup_task_logger.connect(setup_logging)


# Use this function instead of direct access, to allow testing
def get_current_celery_task():
    from celery import current_task
    return current_task


def log_it(ctx_type):

    def logging_decorator(original_function):
        @wraps(original_function)
        def decorated_function(pk, *args, **kwargs):
            original_function_name = original_function.__name__
            task_logger = create_logger(ctx_type, logger, pk)
            task_logger.info("Starting %s for %s %s.", original_function_name, ctx_type, pk)
            result = original_function(pk, *args, **kwargs)
            task_logger.info("Finished %s for %s %s.", original_function_name, ctx_type, pk)
            return result
        return decorated_function

    return logging_decorator


# Celery Tasks working on a Workflow

def process_workflow(workflow_id):
    return chain(create_jobs.s(workflow_id) | process_jobs.s())


@app.task
@log_it('workflow')
def create_jobs(workflow_id):
    workflow = EngineWorkflow.objects.get(pk=workflow_id)
    workflow.create_jobs()
    return workflow.pk


def _process_job(job):
    def dynamicbe_job_chain(job_id):
        return chain(
            provision_fs_be.s(job_id),
            provision_ex_be.s(),
            poll_until_dynbes_ready.s(),
            create_db_tasks.s(),
            spawn_ready_tasks.s())
        # clean_up_dynamic_backends() happens on_job_finished()

    def simple_job_chain(job_id):
        return chain(
            create_db_tasks.s(job_id),
            spawn_ready_tasks.s())

    if job.has_dynamic_backend:
        job_chain = dynamicbe_job_chain(job.pk)
    else:
        job_chain = simple_job_chain(job.pk)

    job_chain.apply_async()


@app.task
@log_it('workflow')
def process_jobs(workflow_id):
    workflow = EngineWorkflow.objects.get(pk=workflow_id)
    if workflow.is_aborting:
        workflow.status = STATUS_ABORTED
        workflow.save()
        return

    for job in workflow.jobs_that_need_processing():
        _process_job(job)


@app.task
@log_it('workflow')
def abort_workflow(workflow_id):
    wfl_logger = create_workflow_logger(logger, workflow_id)
    workflow = EngineWorkflow.objects.get(pk=workflow_id)
    if workflow.status == STATUS_ABORTED:
        return
    not_aborted_tasks = EngineTask.objects.filter(job__workflow__id=workflow.pk).exclude(job__status=STATUS_ABORTED)

    running_tasks = list(filter(lambda x: x.status == STATUS_EXEC, not_aborted_tasks))
    wfl_logger.info("Found %s running tasks", len(running_tasks))
    for task in running_tasks:
        abort_task.apply_async((task.pk,))


@app.task
def on_workflow_completed(workflow_id):
    delete_all_syslog_messages(workflow_id)


# Celery Tasks working on a Job


@app.task(max_retries=None)
@log_it('job')
def provision_fs_be(job_id):
    job_logger = create_job_logger(logger, job_id)
    try:
        provision_be(job_id, 'fs')
        return job_id
    except Exception:
        job_logger.exception("Exception in provision_fs_be for job {0}".format(job_id))
        mark_job_as_error(job_id)
        raise


@app.task(max_retries=None)
@log_it('job')
def provision_ex_be(job_id):
    job_logger = create_job_logger(logger, job_id)
    try:
        provision_be(job_id, 'ex')
        return job_id
    except Exception:
        job_logger.exception("Exception in provision_ex_be for job {0}".format(job_id))
        mark_job_as_error(job_id)
        raise


@app.task(max_retries=None, default_retry_delay=DYNBE_READY_POLL_INTERVAL)
@log_it('job')
def poll_until_dynbes_ready(job_id):
    job_logger = create_job_logger(logger, job_id)
    job = EngineJob.objects.get(pk=job_id)
    if job.is_workflow_aborting:
        abort_job(job)
        return None

    try:
        job_dynbes = job.dynamic_backends.distinct()
        instances_ready = map(provisioning.is_instance_ready, job_dynbes)
        if not all(instances_ready):
            raise get_current_celery_task().retry()

        for dynbe in job_dynbes:
            provisioning.update_dynbe_ip_addresses(job)

        return job_id

    except celery.exceptions.RetryTaskError:
        # raised by the retry above, just re-raise.
        raise
    except Exception:
        job_logger.exception("Error in poll_until_dynbes_ready for job '%s'.", job_id)
        raise get_current_celery_task().retry()


@app.task(max_retries=None)
@log_it('job')
def clean_up_dynamic_backends(job_id):
    job_logger = create_job_logger(logger, job_id)
    try:
        job = EngineJob.objects.get(pk=job_id)
        dynamic_backends = job.dynamicbackendinstance_set.filter(destroyed_on__isnull=True)
        if dynamic_backends.count() == 0:
            logger.info("Job %s has no dynamic backends to be cleaned up.", job_id)
            return
        for dynamic_be in dynamic_backends:
            logger.info("Cleaning up dynamic backend %s", dynamic_be.hostname)
            provisioning.destroy_backend(dynamic_be)

        return job_id
    except Exception:
        job_logger.exception("Exception in clean_up_dynamic_backends for job {0}".format(job_id))
        raise get_current_celery_task().retry()


@app.task(max_retries=None)
@log_it('job')
def create_db_tasks(job_id):
    if job_id is None:
        logger.info("create_db_tasks received no job_id. Skipping processing.")
        return None
    job_logger = create_job_logger(logger, job_id)
    request = get_current_celery_task().request
    try:
        job = EngineJob.objects.get(pk=job_id)
        if job.status == STATUS_READY:
            # Handling case when in a previous execution the Celery worker died
            # after tasks have been created and the transaction has been
            # commited, but the Celery task didn't return yet
            assert job.total_tasks() > 0, "Job in READY state, but has no tasks"
            job_logger.warning("Job was already in READY state. Skipping creation of db tasks.")
            return job_id

        if job.is_workflow_aborting:
            abort_job(job)
            return None

        tasks_count = job.create_tasks()
        if not tasks_count:
            return None
        return job_id

    except DecryptedCredentialNotAvailable as dcna:
        job_logger.exception("Decrypted credential not available.")
        countdown = backoff(request.retries)
        job_logger.warning('create_db_tasks.retry {0} in {1} seconds'.format(job_id, countdown))
        raise get_current_celery_task().retry(exc=dcna, countdown=countdown)
    except Exception:
        job_logger.exception("Exception in create_db_tasks for job {0}".format(job_id))
        mark_job_as_error(job_id)
        raise


@app.task(max_retries=None)
def spawn_ready_tasks(job_id):
    if job_id is None:
        logger.info("spawn_ready_tasks received no job_id. Skipping processing.")
        return None
    job_logger = create_job_logger(logger, job_id)
    job_logger.info("Starting spawn_ready_tasks for Job %s", job_id)
    try:
        job = EngineJob.objects.get(pk=job_id)
        ready_tasks = job.ready_tasks()
        logger.debug(ready_tasks)
        aborting = job.is_workflow_aborting

        if aborting:
            abort_job(job)
            for task in ready_tasks:
                task.set_status(STATUS_ABORTED)
                task.save()
        else:
            spawn_status = {}
            for task in ready_tasks:
                spawn_status[task.pk] = spawn_task(task)
            if not all(spawn_status.values()):
                not_spawned = [e[0] for e in spawn_status.items() if not e[1]]
                job_logger.info("Couldn't spawn tasks: %s", not_spawned)
                current_task = get_current_celery_task()
                current_task.retry(countdown=TASK_LIMIT_REACHED_RETRY_INTERVAL)
            # need to update task.job.status here when all tasks for job spawned ?

        job_logger.info("Finished spawn_ready_tasks for Job %s", job_id)

        return job_id
    except celery.exceptions.RetryTaskError:
        # This is normal operation, Celery is signaling to the Worker
        # that this task should be retried by throwing an RetryTaskError
        # Just re-raise it
        raise
    except Exception:
        job_logger.exception("Exception when spawning tasks for job {0}".format(job_id))
        mark_job_as_error(job_id)
        raise


@app.task
def on_job_finished(job_id):
    job = Job.objects.get(pk=job_id)
    if job.has_dynamic_backend:
        clean_up_dynamic_backends.apply_async((job_id,))


# Celery Tasks working on a Yabi Task

@transaction.commit_on_success()
def spawn_task(task):
    task_logger = create_task_logger(logger, task.pk)
    task_logger.info("Starting spawn_task for task %s.", task.pk)
    if _tasks_per_user_reached_limit(task):
        return False
    task.set_status('requested')
    task.save()
    transaction.commit()
    task_chain = chain(stage_in_files.s(task.pk), submit_task.s(), poll_task_status.s(), stage_out_files.s(), clean_up_task.s())
    task_chain.apply_async()
    task_logger.info("Finished spawn_task for task %s.", task.pk)
    return True


def _tasks_per_user_reached_limit(task):
    exec_backend = task.job.exec_backend
    tasks_per_user = task.job.tool.backend.tasks_per_user
    if tasks_per_user is None:
        # No limits
        return False
    if tasks_per_user == 0:
        logger.info("Can't spawn task %s. Execution backend %s has task_per_user set to 0. No task execution allowed.", task.pk, task.job.exec_backend)
        return True

    running_tasks = running_task_count(be=exec_backend, user=task.job.workflow.user)
    if running_tasks >= tasks_per_user:
        logger.info("Can't spawn task %s. Tasks per user limit reached! Execution backend %s has task_per_user set to %s and there are %s currently running tasks", task.pk, task.job.exec_backend, tasks_per_user, running_tasks)
        return True


def retry_current_celery_task(original_function_name, task_id, exc, countdown, polling_task=False):
    task_logger = create_task_logger(logger, task_id)
    task_logger.warning('{0}.retry {1} in {2} seconds'.format(original_function_name, task_id, countdown))
    try:
        current_task = get_current_celery_task()
        current_task.retry(exc=exc, countdown=countdown)
    except celery.exceptions.RetryTaskError:
        # This is normal operation, Celery is signaling to the Worker
        # that this task should be retried by throwing an RetryTaskError
        # Just re-raise it
        try:
            if not polling_task:
                task = Task.objects.get(pk=task_id)
                task.retry_count = current_task.request.retries + 1
                logger.debug("Retry is: %s", current_task.request.retries)
                task.save()
        except Exception:
            # Never fail on saving this
            logger.exception("Failed on saving retry_count for task %d", task_id)
            transaction.rollback()

        raise
    except Exception as ex:
        if ex is exc:
            # The same exception we passed to retry() has been re-raised
            # This means the max_retry limit has been exceeded
            task_logger.error("{0}.retry {1} exceeded retry limit - changing status to error".format(original_function_name, task_id))
        else:
            # Some other Exception occured, log the details
            task_logger.exception(("{0}.retry {1} failed - changing status to error".format(original_function_name, task_id)))

        mark_task_as_error(task_id, str(ex))
        raise


def retry_on_error(original_function):
    @wraps(original_function)
    def decorated_function(task_id, *args, **kwargs):
        task_logger = create_task_logger(logger, task_id)
        request = get_current_celery_task().request
        original_function_name = original_function.__name__

        retry_celery_task = partial(retry_current_celery_task, original_function_name, task_id)
        try:
            result = original_function(task_id, *args, **kwargs)
        except RetryPollingException as exc:
            # constant for polling
            countdown = 30
            retry_celery_task(exc, countdown, polling_task=True)

        except Exception as exc:
            task_logger.exception("Exception in celery task {0} for task {1}".format(original_function_name, task_id))
            mark_task_as_retrying(task_id)
            countdown = backoff(request.retries)
            retry_celery_task(exc, countdown)

        if task_id is not None:
            task_logger.info('Task %s recovered from error' % task_id)
            remove_task_retrying_mark(task_id)

        return result

    return decorated_function


def skip_if_no_task_id(original_function):
    @wraps(original_function)
    def decorated_function(task_id, *args, **kwargs):
        original_function_name = original_function.__name__
        if task_id is None:
            logger.info("%s received no task_id. Skipping processing ", original_function_name)
            return None
        result = original_function(task_id, *args, **kwargs)
        return result

    return decorated_function


@app.task(max_retries=None)
@retry_on_error
@skip_if_no_task_id
@log_it('task')
def stage_in_files(task_id):
    task = EngineTask.objects.get(pk=task_id)
    if abort_task_if_needed(task):
        return None
    change_task_status(task.pk, STATUS_STAGEIN)
    backend.stage_in_files(task)
    return task_id


@app.task(max_retries=MAX_CELERY_TASK_RETRIES)
@retry_on_error
@skip_if_no_task_id
@log_it('task')
def submit_task(task_id):
    task = EngineTask.objects.get(pk=task_id)
    if abort_task_if_needed(task):
        return None
    change_task_status(task.pk, STATUS_EXEC)
    transaction.commit()
    # Re-fetch task
    task = EngineTask.objects.get(pk=task_id)
    backend.submit_task(task)
    return task_id


@app.task(max_retries=None)
@retry_on_error
@skip_if_no_task_id
@log_it('task')
def poll_task_status(task_id):
    task = EngineTask.objects.get(pk=task_id)
    try:
        backend.poll_task_status(task)
        return task_id
    except JobNotFoundException:
        if abort_task_if_needed(task):
            return None
        raise


@app.task(max_retries=None)
@retry_on_error
@skip_if_no_task_id
@log_it('task')
def stage_out_files(task_id):
    task = EngineTask.objects.get(pk=task_id)
    if abort_task_if_needed(task):
        return None
    change_task_status(task.pk, STATUS_STAGEOUT)
    backend.stage_out_files(task)
    return task_id


@app.task(max_retries=None)
@retry_on_error
@skip_if_no_task_id
@log_it('task')
def clean_up_task(task_id):
    task = EngineTask.objects.get(pk=task_id)
    if abort_task_if_needed(task):
        return None
    change_task_status(task.pk, STATUS_CLEANING)
    backend.clean_up_task(task)
    change_task_status(task.pk, STATUS_COMPLETE)


@app.task
@log_it('task')
def abort_task(task_id):
    task = EngineTask.objects.get(pk=task_id)
    backend.abort_task(task)


# Implementation

def abort_task_if_needed(task):
    if task.is_workflow_aborting:
        if task.status != STATUS_ABORTED:
            change_task_status(task.pk, STATUS_ABORTED)
        return True
    return False


def backoff(count=0):
    """
    Provide an exponential backoff with a maximum backoff in seconds
    Used to delay between task retries
    """
    if count > 4:
        count = 4
    return 5 ** (count + 1)


def mark_job_as_error(job_id):
    job = Job.objects.get(pk=job_id)
    wfl_logger = create_workflow_logger(logger, job.workflow.pk)
    job.status = STATUS_ERROR
    job.save()
    job.workflow.update_status()
    wfl_logger.info("Workflow {0} encountered an error.".format(job.workflow.pk))


def mark_task_as_retrying(task_id, message="Some error occurred"):
    task = Task.objects.get(pk=task_id)
    task.mark_task_as_retrying(message)


def remove_task_retrying_mark(task_id):
    task = Task.objects.get(pk=task_id)
    if task.is_retrying:
        task.finished_retrying()


def set_task_error_message(task_id, error_msg):
    task = Task.objects.get(pk=task_id)
    task.error_msg = error_msg
    task.save()


def mark_task_as_error(task_id, error_msg="Some error occured"):
    task_logger = create_task_logger(logger, task_id)
    task_logger.error("Task chain for Task {0} failed with '{1}'".format(task_id, error_msg))
    remove_task_retrying_mark(task_id)
    change_task_status(task_id, STATUS_ERROR)
    set_task_error_message(task_id, error_msg)


def provision_be(job_id, be_type):
    job = EngineJob.objects.get(pk=job_id)
    if job.is_workflow_aborting:
        abort_job(job)
        return None

    def should_use_same_backend(job):
        tool = job.tool
        return (tool.backend.dynamic_backend and
                tool.fs_backend.dynamic_backend and
                tool.use_same_dynamic_backend)

    if be_type == 'ex' and should_use_same_backend(job):
        provisioning.use_fs_backend_for_execution(job)
    else:
        provisioning.create_backend(job, be_type)

    return job_id


def abort_job(job, update_workflow=True):
    job.status = STATUS_ABORTED
    job.save()
    on_job_finished.apply_async((job.pk,))
    if update_workflow:
        job.workflow.update_status()


# Service methods
# TODO TSZ move to another file?


@transaction.commit_manually()
def change_task_status(task_id, status):
    task_logger = create_task_logger(logger, task_id)
    try:
        task_logger.debug("Setting status of task {0} to {1}".format(task_id, status))
        task = Task.objects.get(pk=task_id)
        task.set_status(status)
        task.save()
        transaction.commit()

        job_old_status = task.job.status
        job_status = task.job.update_status()
        job_status_changed = (job_old_status != job_status)

        if job_status_changed:
            transaction.commit()
            old_status = task.job.workflow.status
            task.job.workflow.update_status()
            # commit before submission of Celery Tasks
            transaction.commit()
            if task.job.is_finished:
                on_job_finished.apply_async((task.job.pk,))
            new_status = task.job.workflow.status
            if old_status != new_status and new_status == STATUS_COMPLETE:
                on_workflow_completed.apply_async((task.job.workflow.pk,))
            else:
                process_workflow_jobs_if_needed(task)

        transaction.commit()

    except Exception:
        transaction.rollback()
        task_logger.exception("Exception when updating task's {0} status to {1}".format(task_id, status))
        raise


def process_workflow_jobs_if_needed(task):
    workflow = EngineWorkflow.objects.get(pk=task.job.workflow.pk)
    if workflow.is_aborting:
        for job in workflow.jobs_that_wait_for_dependencies():
            abort_job(job, update_workflow=False)
        workflow.update_status()
        return
    if task.job.status == STATUS_COMPLETE:
        if workflow.has_jobs_to_process():
            process_jobs.apply_async((workflow.pk,))


@log_it('workflow')
@transaction.commit_manually()
def request_workflow_abort(workflow_id, yabiuser=None):
    workflow = EngineWorkflow.objects.get(pk=workflow_id)
    if (workflow.abort_requested_on is not None) or workflow.status in (STATUS_COMPLETE, STATUS_ERROR):
        transaction.commit()
        return False
    workflow.abort_requested_on = datetime.now()
    workflow.abort_requested_by = yabiuser
    workflow.save()
    transaction.commit()
    abort_workflow.apply_async((workflow_id,))
    return True


def delete_all_syslog_messages(workflow_id):
    logger.info("Deleting all the Syslog objects of workflow %s" % workflow_id)
    job_ids = [j.pk for j in Job.objects.filter(workflow__pk=workflow_id)]
    task_ids = [t.pk for t in Task.objects.filter(job__workflow__pk=workflow_id)]

    Syslog.objects.filter(
        Q(table_name='workflow') & Q(table_id=workflow_id) |
        Q(table_name='job') & Q(table_id__in=job_ids) |
        Q(table_name='task') & Q(table_id__in=task_ids)
    ).delete()


def running_task_count(be, user):
    running_tasks = Task.objects.filter(job__workflow__user=user, job__exec_backend=be,
                                        status_requested__isnull=False,
                                        status_complete__isnull=True,
                                        status_error__isnull=True,
                                        status_exec_error__isnull=True,
                                        status_aborted__isnull=True,
                                        status_blocked__isnull=True).count()

    return running_tasks
