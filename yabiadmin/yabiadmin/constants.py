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
"""project constants.

Things that don't really belong in settings because they never change, you know!
"""

# status settings that can be used on workflow, job and task.
STATUS = ['pending','ready','requested','running','complete','error','blocked','resume','rewalk']

# constants
STATUS_PENDING = 'pending'
STATUS_READY = 'ready'
STATUS_REQUESTED = 'requested'
STATUS_RUNNING = 'running'
STATUS_COMPLETE = 'complete'
STATUS_ERROR = 'error'
STATUS_EXEC_ERROR = 'exec:error'
STATUS_BLOCKED = 'blocked'
STATUS_RESUME = 'resume'
STATUS_REWALK = 'rewalk'


STATUS_TASKS_CREATED = "tasks created"
STATUS_TASKS_SPAWNED = "tasks spawned"


STATUS_EXEC = 'exec'
STATUS_STAGEOUT = 'stageout'
STATUS_STAGEIN = 'stagein'
STATUS_CLEANING = 'cleaning'

STATUS_MAP = (
    (STATUS_PENDING, 0.0),
    (STATUS_READY, 0.0),
    (STATUS_REQUESTED, 0.01),
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
    (STATUS_COMPLETE, 1.0),

    # Added to allow tasks to be created without a status. Tasks may be created without status
    # at the very beginning and then have their status chanegd
    ('', 0.1),
)


STATUS_PROGRESS_MAP = dict(STATUS_MAP)

_statuses_order = [st[0] for st in STATUS_MAP if st[0] != ''] + [STATUS_BLOCKED]
_statuses_order.reverse()
STATUSES_REVERSE_ORDER = _statuses_order

# validation settings, these reflect the types of backend that yabi can handle
EXEC_SCHEMES = ['sge', 'torque', 'ssh', 'ssh+pbspro', 'ssh+torque', 'ssh+sge', 'localex','explode','null']
FS_SCHEMES = ['http', 'https', 'yabifs', 'scp', 'sftp', 's3', 'localfs', 'file', 'null']
VALID_SCHEMES = EXEC_SCHEMES + FS_SCHEMES

# Celery Settings
MAX_CELERY_TASK_RETRIES = 3

