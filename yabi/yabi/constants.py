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
"""project constants.

Things that don't really belong in settings because they never change, you know!
"""

# status settings that can be used on workflow, job and task.
STATUS = ['pending', 'ready', 'requested', 'running', 'complete', 'error', 'blocked', 'aborted', 'resume', 'rewalk']

# constants
STATUS_PENDING = 'pending'
STATUS_READY = 'ready'
STATUS_REQUESTED = 'requested'
STATUS_RUNNING = 'running'
STATUS_COMPLETE = 'complete'
STATUS_ERROR = 'error'
STATUS_EXEC_ERROR = 'exec:error'
STATUS_BLOCKED = 'blocked'
STATUS_ABORTED = 'aborted'
STATUS_RESUME = 'resume'
STATUS_REWALK = 'rewalk'


JOB_STATUS_PROCESSING = "started processing"  # Job has begun, but has not yet created Task objects or spawned chains.
JOB_STATUS_TASKS_SPAWNED = "tasks spawned"    # Job has created Task objects and spawned chains.


STATUS_EXEC = 'exec'
STATUS_STAGEOUT = 'stageout'
STATUS_STAGEIN = 'stagein'
STATUS_CLEANING = 'cleaning'

STATUS_MAP = (
    (STATUS_PENDING, 0.0),
    (STATUS_READY, 0.0),
    (STATUS_REQUESTED, 0.01),
    (JOB_STATUS_PROCESSING, 0.02),
    (JOB_STATUS_TASKS_SPAWNED, 0.03),
    (STATUS_STAGEIN, 0.05),
    ('mkdir', 0.1),
    (STATUS_EXEC, 0.11),
    ('exec:unsubmitted', 0.12),
    ('exec:pending', 0.13),
    ('exec:active', 0.2),
    ('exec:running', 0.2),
    ('exec:cleanup', 0.7),
    ('exec:done', 0.75),
    (STATUS_STAGEOUT, 0.8),
    (STATUS_CLEANING, 0.9),

    ('error', 0.0),
    ('exec:error', 0.0),
    (STATUS_ABORTED, 0.0),
    (STATUS_COMPLETE, 1.0),

    # Added to allow tasks to be created without a status. Tasks may be created without status
    # at the very beginning and then have their status chanegd
    ('', 0.1),
)


STATUS_PROGRESS_MAP = dict(STATUS_MAP)

_statuses_order = [st[0] for st in STATUS_MAP
                   if st[0] != '' and st[0] not in (JOB_STATUS_PROCESSING, JOB_STATUS_TASKS_SPAWNED)] + [STATUS_BLOCKED]
_statuses_order.reverse()
STATUSES_REVERSE_ORDER = _statuses_order

TERMINATED_STATUSES = (STATUS_COMPLETE, STATUS_ERROR, STATUS_EXEC_ERROR, STATUS_ABORTED)

# Celery Settings
MAX_CELERY_TASK_RETRIES = 3

ENVVAR_FILENAME = '.envvars.yabi'
