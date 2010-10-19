# -*- coding: utf-8 -*-

from django.http import HttpResponse
from yabiadmin.yabi import models
from django.utils import simplejson as json

from yabiadmin.yabistoreapp import db
from yabiadmin.yabiengine.tasks import build
from yabiadmin.yabiengine.enginemodels import EngineWorkflow

from decorators import memcache, authentication_required

import logging
logger = logging.getLogger('yabiadmin')

class YabiError(StandardError):
    pass

@authentication_required
def submitjob(request):
    logger.debug(request.user.username)

    # TODO extract common code from here and submitworkflow

    try:
        job = create_job(request)
        workflow_dict = create_wrapper_workflow(job)
        workflow_json = json.dumps(workflow_dict)
        user = models.User.objects.get(name=request.user.username)

        workflow = EngineWorkflow(name=workflow_dict["name"], json=workflow_json, user=user)
        workflow.save()

        # put the workflow in the store
        db.save_workflow(user.name, workflow.workflow_id, workflow_json, workflow.status, workflow.name)
    
        # trigger a build via celery
        build.delay(workflow_id=workflow.id)

        resp = {'success': True, 'workflow_id':workflow.id}
    except YabiError, e:
        resp = {'success': False, 'msg': str(e)}

    return HttpResponse(json.dumps(resp))

# Implementation

def create_job(request):
    toolname = request.POST.get('name')
    tools = models.Tool.objects.filter(name=toolname)
    if len(tools) == 0:
        raise YabiError('Unknown tool name "%s"' % toolname)
    tool = tools[0]    
    return {'toolName': tool.name, 'jobId': 1, 'valid': True, 
            'parameterList': {'parameter': []}}

def create_wrapper_workflow(job):
    def generate_name(job):
        return job['toolName']

    workflow = {
        'name': generate_name(job),
        'tags': ['yabish'],
        'jobs': [job]
    }
    
    return workflow    

