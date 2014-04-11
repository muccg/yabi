from django.utils import unittest as unittest

from model_mommy import mommy

from yabiadmin.yabiengine.models import Syslog
from yabiadmin.yabiengine.engine_logging import create_task_logger, create_job_logger, create_workflow_logger

import logging

MSG = "A logging message"
WORKFLOW_ID = 10
JOB_ID = 50
TASK_ID = 100


class YabiDBHandlerNormalLoggingTest(unittest.TestCase):

    def test_not_logging_without_adapter(self):
        logger = logging.getLogger('yabiadmin.yabiengine')
        logger.debug(MSG)
        self.assertEquals(0, Syslog.objects.filter(message=MSG).count())


class YabiDBHandlerLoggingTest(unittest.TestCase):


    def tearDown(self):
        Syslog.objects.filter(message=MSG).delete()


    def test_logging_with_task_logger(self):
        logger = logging.getLogger('yabiadmin.yabiengine')
        task_logger = create_task_logger(logger, TASK_ID)

        task_logger.debug(MSG)

        self.assertEquals(1, Syslog.objects.filter(message=MSG).count(), "Message should been syslogged")
        syslog = Syslog.objects.get(message=MSG)
        self.assertEquals('task', syslog.table_name)
        self.assertEquals(TASK_ID, syslog.table_id)

    def test_logging_should_work_for_every_yabiadmin_logger(self):
        NAMES = ('yabiadmin', 'yabiadmin.backend', 'yabiadmin.yabi.models')
        loggers = map(logging.getLogger, NAMES)
        task_loggers = map(lambda l: create_task_logger(l, TASK_ID), loggers)

        for task_logger in task_loggers:
            task_logger.debug(MSG)

        self.assertEquals(len(NAMES), Syslog.objects.filter(message=MSG).count(), "All loggers should log to Syslog")

    def test_logging_with_job_logger(self):
        logger = logging.getLogger('yabiadmin.backend.celerytasks')
        job_logger = create_job_logger(logger, JOB_ID)

        job_logger.debug(MSG)

        self.assertEquals(1, Syslog.objects.filter(message=MSG).count(), "Message should been syslogged")
        syslog = Syslog.objects.get(message=MSG)
        self.assertEquals('job', syslog.table_name)
        self.assertEquals(JOB_ID, syslog.table_id)

    def test_logging_with_workflow_logger(self):
        logger = logging.getLogger('yabiadmin.backend.celerytasks')
        wfl_logger = create_workflow_logger(logger, WORKFLOW_ID)

        wfl_logger.debug(MSG)

        self.assertEquals(1, Syslog.objects.filter(message=MSG).count(), "Message should been syslogged")
        syslog = Syslog.objects.get(message=MSG)
        self.assertEquals('workflow', syslog.table_name)
        self.assertEquals(WORKFLOW_ID, syslog.table_id)


