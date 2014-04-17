from django.utils import unittest as unittest
from django.conf import settings

import celery
from celery import _state
from mockito import *
from model_mommy import mommy

from yabiadmin.backend import celerytasks
from yabiadmin.yabi import models as m
from yabiadmin.constants import STATUS_ERROR
from yabiadmin.yabiengine.models import Task, Syslog
from yabiadmin.yabiengine.engine_logging import create_workflow_logger, create_job_logger, create_task_logger, YabiDBHandler
from yabiadmin.backend.celerytasks import retry_on_error
from yabiadmin.backend.exceptions import RetryException, RetryPollingException

import logging

logger = logging.getLogger(__name__)


def create_workflow_with_job_and_a_task(obj):
    demo_user = m.User.objects.get(name='demo')
    obj.workflow = mommy.make('Workflow', user=demo_user)
    obj.job = mommy.make('Job', workflow=obj.workflow, pk=obj.workflow.pk, order=0)
    obj.task = mommy.make('Task', job=obj.job, pk=obj.job.pk)
    obj.tool = mommy.make('Tool', name='my-tool', path='tool.sh')


def delete_models(*args):
    for model in args:
        model.delete()


class FakeRequest(object):
    def __init__(self, retries=None):
        self.retries = 0 if retries is None else retries
        self.exception = None
        self.countdown = None

class FakeCeleryTask(object):
    def __init__(self, retries=None):
        self.request = FakeRequest(retries)
        self.max_retries_exceeded = False
        self.celery_errors_on_retry = False

    def retry(self, exc=None, countdown=None):
        self.exception = exc
        self.countdown = countdown
        if self.celery_errors_on_retry:
            raise self.celery_exception
        elif self.max_retries_exceeded:
            raise exc

        raise celery.exceptions.RetryTaskError()

    def simulate_max_retries_exceeded(self):
        self.max_retries_exceeded = True

    def simulate_celery_errors_on_retry(self, exc=None):
        self.celery_exception = exc if exc is not None else Exception("celery")
        self.celery_errors_on_retry = True


class RetryOnErrorTest(unittest.TestCase):

    def setUp(self):
        self.celery_current_task = FakeCeleryTask()

        create_workflow_with_job_and_a_task(self)

    def tearDown(self):
        delete_models(self.workflow, self.tool)

    def test_when_no_exceptions_returns_what_wrapped_fn_returns(self):
        self.setup_function_that_succeeds()

        result = self.retrying_fn(self.task.pk)

        self.assertEquals(self.task.pk, result)

    def test_when_Exception_task_is_retried(self):
        self.setup_function_that_errors()

        with self.assertRaises(celery.exceptions.RetryTaskError):
            self.retrying_fn(self.task.pk)
        self.assertIs(self.my_exception, self.celery_current_task.exception, "Should been called with our exception")
        self.assertEquals(5, self.celery_current_task.countdown, "Should retry in 5 seconds")

    def test_retry_is_backing_off_on_subsequent_retries(self):
        self.setup_function_that_errors()

        retry_delay_when_failed_with = self.retry_delay_when_failed_with

        self.assertEquals(   5, retry_delay_when_failed_with(retries=0))
        self.assertEquals(  25, retry_delay_when_failed_with(retries=1))
        self.assertEquals( 125, retry_delay_when_failed_with(retries=2))
        self.assertEquals( 625, retry_delay_when_failed_with(retries=3))
        self.assertEquals(3125, retry_delay_when_failed_with(retries=4))
        self.assertEquals(3125, retry_delay_when_failed_with(retries=5))
        self.assertEquals(3125, retry_delay_when_failed_with(retries=100))

    def test_when_RetryPollingException_retry_delays_are_constant(self):
        self.setup_function_that_errors(exception=RetryPollingException())

        retry_delay_when_failed_with = self.retry_delay_when_failed_with

        # Polling should always be retried after 30 seconds
        self.assertEquals(30, retry_delay_when_failed_with(retries=0))
        self.assertEquals(30, retry_delay_when_failed_with(retries=0))
        self.assertEquals(30, retry_delay_when_failed_with(retries=0))

    def test_retrying_task_recovers_from_error(self):
        self.setup_function_that_succeeds()

        self.celery_current_task.request.retries = 1
        self.task.mark_task_as_retrying("A previous error")

        result = self.retrying_fn(self.task.pk)

        reloaded_task = Task.objects.get(pk=self.task.pk)
        self.assertFalse(reloaded_task.is_retrying)
        self.assertIsNone(reloaded_task.error_msg)

    def test_task_is_marked_as_errored_when_max_retries_is_exceeded(self):
        self.setup_function_that_errors(ValueError("just an exception"))

        self.celery_current_task.simulate_max_retries_exceeded()
        self.celery_current_task.request.retries = 3
        self.task.mark_task_as_retrying("A previous error")

        with self.assertRaises(ValueError):
            self.retrying_fn(self.task.pk)

        reloaded_task = Task.objects.get(pk=self.task.pk)

        self.assertEqual(STATUS_ERROR, reloaded_task.status)
        self.assertEqual(STATUS_ERROR, reloaded_task.job.status)
        self.assertEqual(STATUS_ERROR, reloaded_task.job.workflow.status)
        self.assertFalse(reloaded_task.is_retrying, "Shouldn't be marked as retrying anymore")
        self.assertEqual("just an exception", reloaded_task.error_msg)


    def test_task_is_marked_as_errored_when_celery_error_on_retry(self):
        self.setup_function_that_errors(ValueError("just an exception"))

        celery_exc = RuntimeError("a celery exception")
        self.celery_current_task.simulate_celery_errors_on_retry(celery_exc)
        self.celery_current_task.request.retries = 3
        self.task.mark_task_as_retrying("A previous error")

        with self.assertRaises(RuntimeError):
            self.retrying_fn(self.task.pk)

        reloaded_task = Task.objects.get(pk=self.task.pk)

        self.assertEqual(STATUS_ERROR, reloaded_task.status)
        self.assertEqual(STATUS_ERROR, reloaded_task.job.status)
        self.assertEqual(STATUS_ERROR, reloaded_task.job.workflow.status)
        self.assertFalse(reloaded_task.is_retrying, "Shouldn't be marked as retrying anymore")
        self.assertEqual("a celery exception", reloaded_task.error_msg)


    def setup_function_that_succeeds(self):
        def wrapped_fn(task_id):
            return task_id

        when(celerytasks).get_current_celery_task().thenReturn(self.celery_current_task)

        self.retrying_fn = retry_on_error(wrapped_fn)

    def setup_function_that_errors(self, exception=None):
        self.my_exception = Exception() if exception is None else exception
        def wrapped_fn(task_id):
            raise self.my_exception

        when(celerytasks).get_current_celery_task().thenReturn(self.celery_current_task)

        self.retrying_fn = retry_on_error(wrapped_fn)

    def retry_delay_when_failed_with(self, retries=None):
        self.celery_current_task.request.retries = retries
        with self.assertRaises(celery.exceptions.RetryTaskError):
            self.retrying_fn(self.task.pk)
        return self.celery_current_task.countdown


class DeleteAllSyslogMessagesTest(unittest.TestCase):

    def setUp(self):
        logger.addHandler(YabiDBHandler())
        create_workflow_with_job_and_a_task(self)
        self.wfl_logger = create_workflow_logger(logger, self.workflow.pk)
        self.job_logger = create_job_logger(logger, self.job.pk)
        self.task_logger = create_task_logger(logger, self.task.pk)
        self.other_wfl_logger = create_workflow_logger(logger, self.workflow.pk + 1)
        self.other_job_logger = create_job_logger(logger, self.job.pk + 1)
        self.other_task_logger = create_task_logger(logger, self.task.pk + 1)

    def tearDown(self):
        self.delete_log_messages()
        delete_models(self.workflow, self.tool)

    def delete_log_messages(self):
        Syslog.objects.filter(table_name='workflow', table_id__in=(self.workflow.pk, self.workflow.pk+1)).delete()
        Syslog.objects.filter(table_name='job', table_id__in=(self.job.pk, self.job.pk+1)).delete()
        Syslog.objects.filter(table_name='task', table_id__in=(self.task.pk, self.task.pk+1)).delete()
        Syslog.objects.filter(table_name='task', table_id__in=(self.task.pk, self.workflow.pk)).delete()

    def test_no_syslog_messages_to_start_with(self):
        self.assertEquals(0, Syslog.objects.filter(table_name='workflow', table_id=self.workflow.pk).count())
        self.assertEquals(0, Syslog.objects.filter(table_name='job', table_id=self.job.pk).count())
        self.assertEquals(0, Syslog.objects.filter(table_name='task', table_id=self.task.pk).count())

    def log_some_messages(self):
        self.wfl_logger.debug('Some message')
        self.wfl_logger.debug('Some other message')
        self.job_logger.debug('Some job level message')
        self.task_logger.debug('Some task level message')
        self.task_logger.debug('Some other task level message')
        self.task_logger.debug('And another task level message')

    def log_some_other_messages(self):
        self.other_wfl_logger.debug('Some message')
        self.other_job_logger.debug('Some job level message')
        self.other_task_logger.debug('Some task level message')

    def test_logger_logs_properly(self):
        self.log_some_messages()

        self.assertEquals(2, Syslog.objects.filter(table_name='workflow', table_id=self.workflow.pk).count())
        self.assertEquals(1, Syslog.objects.filter(table_name='job', table_id=self.job.pk).count())
        self.assertEquals(3, Syslog.objects.filter(table_name='task', table_id=self.task.pk).count())

    def test_log_messages_are_deleted(self):
        self.log_some_messages()

        celerytasks.delete_all_syslog_messages(self.workflow.pk)

        self.assertEquals(0, Syslog.objects.filter(table_name='workflow', table_id=self.workflow.pk).count())
        self.assertEquals(0, Syslog.objects.filter(table_name='job', table_id=self.job.pk).count())
        self.assertEquals(0, Syslog.objects.filter(table_name='task', table_id=self.task.pk).count())

    def test_only_the_associated_messages_are_deleted(self):
        self.log_some_messages()
        self.log_some_other_messages()

        log_count = Syslog.objects.count()

        celerytasks.delete_all_syslog_messages(self.workflow.pk)

        after_delete_log_count = Syslog.objects.count()

        self.assertEquals(6, log_count - after_delete_log_count, "Only 6 log messages should be deleted")


