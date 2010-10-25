# -*- coding: utf-8 -*-
"""project constants.

Things that don't really belong in settings because they never change, you know!
"""

# status settings that can be used on workflow, job and task.
STATUS = ['pending','ready','requested','running','complete','error','blocked']

# constants
STATUS_PENDING = 'pending'
STATUS_READY = 'ready'
STATUS_REQUESTED = 'requested'
STATUS_RUNNING = 'running'
STATUS_COMPLETE = 'complete'
STATUS_ERROR = 'error'
STATUS_BLOCKED = 'blocked'

STATUS_PROGRESS_MAP = {
    'pending':0.0,
    'ready':0.0,
    'requested':0.01,
    'stagein':0.05,
    'mkdir':0.1,
    'exec':0.11,
    'exec:unsubmitted':0.12,
    'exec:pending':0.13,
    'exec:active':0.2,
    'exec:running':0.2,
    'exec:cleanup':0.7,
    'exec:done':0.75,
    'exec:error':0.0,
    'stageout':0.8,
    'cleaning':0.9,
    'complete':1.0,
    'error':0.0,

    # Added to allow tasks to be created without a status. Tasks may be created without status
    # at the very beginning and then have their status chanegd
    '':0.0
    }