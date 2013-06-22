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
from yabiadmin.yabiengine.enginemodels import EngineWorkflow
from yabiadmin.yabi.models import DecryptedCredentialNotAvailable
from yabiadmin.constants import STATUS_REWALK, STATUS_ERROR
import traceback
from django.db import transaction
import celery
from celery import current_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# backoff in seconds
def backoff(count=0):
    if count > 4:
        count = 4
    return 5 ** (count + 1)


# Build a workflow then walk it
def build_workflow(workflow_id):
    chain = build.s(workflow_id) | walk.s()
    chain()


# TODO Make idempotent
# select for update on a build status
#
@celery.task(ignore_result=True)
def build(workflow_id):
    assert(workflow_id)
    request = current_task.request
    try:
        workflow = EngineWorkflow.objects.get(id=workflow_id)
        workflow.build()
    except Exception, exc:
        logger.error(exc)
        workflow.status = STATUS_ERROR
        workflow.save()
        raise exc
    return workflow_id


# TODO Make idempotent
# select for update on a walking status
#
@celery.task(ignore_result=True, max_retries=None)
def walk(workflow_id):
    assert(workflow_id)
    request = current_task.request
    try:
        workflow = EngineWorkflow.objects.get(id=workflow_id)
        workflow.walk()
    except DecryptedCredentialNotAvailable, dcna:
        logger.error("Decrypted credential not available.")
        logger.error(dcna)
        countdown = backoff(request.retries)
        logger.debug('walk.retry {0} in {1} seconds'.format(workflow_id, countdown))
        raise walk.retry(exc=dcna, countdown=countdown)
    except Exception, exc:
        logger.error(exc)
        workflow.status = STATUS_ERROR
        workflow.save()
        raise exc
    return workflow_id
