# -*- coding: utf-8 -*-
from celery.decorators import task
from yabiadmin.yabiengine.enginemodels import EngineWorkflow

@task
def build(workflow_id):
    print "BUILD:",workflow_id
    assert(workflow_id)
    eworkflow = EngineWorkflow.objects.get(id=workflow_id)
    eworkflow.build()
    print "------------->"
    eworkflow.walk()
    return workflow_id

@task
def walk(workflow_id):
    print "WALK:",workflow_id
    assert(workflow_id)
    eworkflow = EngineWorkflow.objects.get(id=workflow_id)
    eworkflow.walk()
    return workflow_id
