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
