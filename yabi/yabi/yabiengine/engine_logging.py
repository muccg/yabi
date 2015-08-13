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

import os
import logging
from functools import partial

# Use the create_TYPE_logger methods to create loggers that add context to all
# messages logged with that logger.
#
# Ex:
#
# logger = logging.getLogger(__name__) # Usually defined at top of module
#
# task_logger.create_task_logger(logger, 100)
# task_logger.info("Stagein started.")
#
# The "Stageing started" LogRecord will be associated with Task 100.
#
# YabiDBHandler is configured in settings.py to log all the LogRecords with
# context to the yabi.yabiengine.models.Syslog


logger = logging.getLogger(__name__)


def create_logger(context_type, logger, pk):
    return logging.LoggerAdapter(logger, {
        'yabi_context': {
            'type': context_type,
            'id': pk}})


create_workflow_logger = partial(create_logger, 'workflow')
create_job_logger = partial(create_logger, 'job')
create_task_logger = partial(create_logger, 'task')


class YabiDBHandler(logging.Handler):

    def emit(self, record):
        from yabi.yabiengine import models as m
        if hasattr(record, 'yabi_context'):
            table_name = record.yabi_context.get('type')
            table_id = record.yabi_context.get('id')
            try:
                m.Syslog.objects.create(
                    message=self.format_message(record),
                    table_name=table_name,
                    table_id=table_id)
            except:
                logger.exception("Couldn't log to Syslog table")
                logger.error("Original message %s", self.format_message(record))

    def format_message(self, record):
        msg = record.getMessage()
        if record.exc_info is not None:
            formatter = logging.Formatter()
            traceback = formatter.formatException(record.exc_info)
            msg = msg.rstrip()
            msg = os.linesep.join((msg, traceback))

        return msg


class YabiContextFilter(logging.Filter):

    def filter(self, record):
        return hasattr(record, 'yabi_context')
