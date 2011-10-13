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
from celery.task import task
from yabiadmin.yabiengine.enginemodels import EngineWorkflow
from yabiadmin.yabi.models import DecryptedCredentialNotAvailable
from constants import STATUS_REWALK, STATUS_ERROR
import traceback

@task(name="yabiadmin.yabiengine.tasks.build")
def build(workflow_id):
    print "BUILD: ",workflow_id
    assert(workflow_id)
    eworkflow = EngineWorkflow.objects.get(id=workflow_id)
    print "building...",eworkflow
    eworkflow.build()
    print "------------->"
    eworkflow.walk()
    return workflow_id

#@task(name="yabiadmin.yabiengine.tasks.walk")
class walk(Task):
    ignore_result = True

    @transaction.commit_on_success
    def run(self, workflow_id, **kwargs):
        print "WALK:",workflow_id
        assert(workflow_id)
        eworkflow = EngineWorkflow.objects.get(id=workflow_id)
        try:
            eworkflow.walk()
        except DecryptedCredentialNotAvailable,dcna:
            print "Walk failed due to decrypted credential not being available. Will re-walk on decryption. Exception was %s"%dcna
            eworkflow.status = STATUS_REWALK
            eworkflow.save()
        except Exception, e:
            eworkflow.status = STATUS_ERROR
            eworkflow.save()
            raise
        return workflow_id
