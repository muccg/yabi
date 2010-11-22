# -*- coding: utf-8 -*-
from celery.decorators import task
from yabiadmin.yabiengine.enginemodels import EngineWorkflow
from yabiadmin.yabi.models import DecryptedCredentialNotAvailable
from constants import STATUS_REWALK

@task
def build(workflow_id):
    print "BUILD:",workflow_id
    assert(workflow_id)
    eworkflow = EngineWorkflow.objects.get(id=workflow_id)
    print "building...",eworkflow
    eworkflow.build()
    print "------------->"
    eworkflow.walk()
    return workflow_id

@task
def walk(workflow_id):
    print "WALK:",workflow_id
    assert(workflow_id)
    eworkflow = EngineWorkflow.objects.get(id=workflow_id)
    try:
        eworkflow.walk()
    except DecryptedCredentialNotAvailable,dcna:
        print "Walk failed due to decrypted credential not being available. Will re-walk on decryption. Exception was %s"%dcna
        eworkflow.status = STATUS_REWALK
        eworkflow.save()
    return workflow_id
