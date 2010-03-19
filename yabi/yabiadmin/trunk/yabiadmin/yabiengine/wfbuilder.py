# -*- coding: utf-8 -*-
import datetime
import os

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.conf import settings
from django.utils import simplejson as json

from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog, StageIn
from yabiadmin.yabiengine.enginemodels import EngineTask, EngineJob, EngineWorkflow
from yabiadmin.yabmin.models import Backend, BackendCredential, Tool, User
from yabiadmin.yabiengine.YabiJobException import YabiJobException
from yabiadmin.yabiengine import backendhelper


import logging
logger = logging.getLogger('yabiengine')


def build(username, workflow_json):
    logger.debug('')
    
    workflow_dict = json.loads(workflow_json)

    try:

        user = User.objects.get(name=username)

        # TODO comment why this save is needed
        workflow = EngineWorkflow(name=workflow_dict["name"], json=workflow_json, user=user)
        workflow.save()

        # sort out the stageout directory
        if 'default_stageout' in workflow_dict and workflow_dict['default_stageout']:
            default_stageout = workflow_dict['default_stageout']
        else:
            default_stageout = user.default_stageout
            
        workflow.stageout = "%s%s/" % (default_stageout, workflow.name)
        workflow.status = settings.STATUS['ready']
        workflow.save()

        # TODO I dont this should be here, rather than calling backends, make the backends do it
        backendhelper.mkdir(workflow.user.name, workflow.stageout)

        # save the jobs
        for i,job_dict in enumerate(workflow_dict["jobs"]):
            job = EngineJob(workflow=workflow, order=i, start_time=datetime.datetime.now())
            job.addJob(job_dict)

        # start processing
        logger.debug('-----Starting workflow id %d -----' % workflow.id)
        workflow.walk()

        return workflow.yabistore_id
    

    except ObjectDoesNotExist, e:
        logger.critical(e)
        import traceback
        logger.debug(traceback.format_exc())        
        raise
    except KeyError, e:
        logger.critical(e)
        import traceback
        logger.debug(traceback.format_exc())        
        raise
    except Exception, e:
        logger.critical(e)
        import traceback
        logger.debug(traceback.format_exc())
        raise
