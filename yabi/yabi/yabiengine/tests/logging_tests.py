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

import unittest
from yabi.yabiengine.models import Syslog
from yabi.yabiengine.engine_logging import create_task_logger, create_job_logger, create_workflow_logger, YabiDBHandler

import logging

MSG = "A logging message"
WORKFLOW_ID = 10
JOB_ID = 50
TASK_ID = 100


class MyVerySpecificException(StandardError):
    pass


class YabiDBHandlerNormalLoggingTest(unittest.TestCase):

    def setUp(self):
        logger = logging.getLogger('yabi')
        logger.addHandler(YabiDBHandler())

    def test_not_logging_without_adapter(self):
        logger = logging.getLogger('yabi.yabiengine')
        logger.debug(MSG)
        self.assertEquals(0, Syslog.objects.filter(message=MSG).count())


class YabiDBHandlerLoggingTest(unittest.TestCase):

    def setUp(self):
        logger = logging.getLogger('yabi')
        logger.addHandler(YabiDBHandler())

    def tearDown(self):
        Syslog.objects.filter(message=MSG).delete()
        Syslog.objects.filter(message__startswith="Exception caught").delete()

    def test_logging_with_task_logger(self):
        logger = logging.getLogger('yabi.yabiengine')
        task_logger = create_task_logger(logger, TASK_ID)

        task_logger.debug(MSG)

        self.assertEquals(1, Syslog.objects.filter(message=MSG).count(), "Message should been syslogged")
        syslog = Syslog.objects.get(message=MSG)
        self.assertEquals('task', syslog.table_name)
        self.assertEquals(TASK_ID, syslog.table_id)

    def test_logging_should_work_for_every_yabi_logger(self):
        NAMES = ('yabi', 'yabi.backend', 'yabi.yabi.models')
        loggers = map(logging.getLogger, NAMES)
        task_loggers = map(lambda l: create_task_logger(l, TASK_ID), loggers)

        for task_logger in task_loggers:
            task_logger.debug(MSG)

        self.assertEquals(len(NAMES), Syslog.objects.filter(message=MSG).count(), "All loggers should log to Syslog")

    def test_logging_with_job_logger(self):
        logger = logging.getLogger('yabi.backend.celerytasks')
        job_logger = create_job_logger(logger, JOB_ID)

        job_logger.debug(MSG)

        self.assertEquals(1, Syslog.objects.filter(message=MSG).count(), "Message should been syslogged")
        syslog = Syslog.objects.get(message=MSG)
        self.assertEquals('job', syslog.table_name)
        self.assertEquals(JOB_ID, syslog.table_id)

    def test_logging_with_workflow_logger(self):
        logger = logging.getLogger('yabi.backend.celerytasks')
        wfl_logger = create_workflow_logger(logger, WORKFLOW_ID)

        wfl_logger.debug(MSG)

        self.assertEquals(1, Syslog.objects.filter(message=MSG).count(), "Message should been syslogged")
        syslog = Syslog.objects.get(message=MSG)
        self.assertEquals('workflow', syslog.table_name)
        self.assertEquals(WORKFLOW_ID, syslog.table_id)

    def test_exception_info_is_logged(self):
        logger = logging.getLogger('yabi')
        wfl_logger = create_workflow_logger(logger, WORKFLOW_ID)

        try:
            raise MyVerySpecificException("my error message")
        except MyVerySpecificException:
            wfl_logger.exception("Exception caught")

        syslog = Syslog.objects.get(table_name='workflow', table_id=WORKFLOW_ID, message__startswith="Exception caught")

        self.assertTrue('MyVerySpecificException' in syslog.message, "Information about the exception should be logged")
        self.assertTrue('my error message' in syslog.message, "The excpetions value should be logged")
