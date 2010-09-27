# -*- coding: utf-8 -*-
import httplib, os
import uuid
from urllib import urlencode
from os.path import splitext

from django.conf import settings
from django.utils import simplejson as json

import logging
logger = logging.getLogger('yabiengine')

def updateWorkflow(workflow, workflow_json=None):

    # if no json for workflow provided, pull down the existing one
    # TODO This is a real hack
    if not workflow_json:
        get_status, get_data = getWorkflow(workflow)
        if get_status != 200:
            return get_status, get_data
        json_object = json.loads(get_data)
        workflow_json = json.dumps(json_object['json'])

    resource = os.path.join(settings.YABISTORE_BASE,"workflows", workflow.user.name, str(workflow.id))
    data = {'json':workflow_json,
            'name':workflow.name,
            'status':workflow.status
            }

    data = urlencode(data)
    headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
    conn = httplib.HTTPConnection(settings.YABISTORE_SERVER)
    conn.request('POST', resource, data, headers)
    logger.debug("store post: %s" % resource)
    r = conn.getresponse()
    status = r.status
    data = r.read()
    logger.debug("store post: %s" % status)

    return status,data

def getWorkflow(workflow):
    ''' Get the JSON for the given workflow
    '''
    resource = os.path.join(settings.YABISTORE_BASE,"workflows", workflow.user.name, str(workflow.id))
    conn = httplib.HTTPConnection(settings.YABISTORE_SERVER)
    conn.request('GET', resource)
    logger.debug("store get: %s" % resource)
    r = conn.getresponse()
    status = r.status
    data = r.read()
    logger.debug("store get: %s" % status)
    return status,data

def updateJob(job, snippet={}):
    ''' Within a workflow, update a job snippet of the form:
            {'tasksComplete':1.0,
                'tasksTotal':1.0
            }

        Also does status & stageout from the job
    '''
    # get the workflow that needs updating
    status, data = getWorkflow(job.workflow)
    assert(status == 200)
    assert(data)
    json_object = json.loads(data)

    job_id = int(job.order)
    assert json_object['json']['jobs'][job_id]['jobId'] == job_id + 1 # jobs are 1 indexed in json

    # status
    json_object['json']['jobs'][job_id]['status'] = job.status

    # data
    for key in snippet:
        json_object['json']['jobs'][job_id][key] = snippet[key]

    # stageout
    if job.stageout:
        json_object['json']['jobs'][job_id]['stageout'] = job.stageout

    # save the workflow json in the store
    updateWorkflow(job.workflow, json.dumps(json_object['json']))

def deleteWorkflow(workflow):
    ''' Delete all references to a workflow from the store.
    '''
    logger.debug('')
    resource = os.path.join(settings.YABISTORE_BASE,"workflows/delete", workflow.user.name, str(workflow.id))
    conn = httplib.HTTPConnection(settings.YABISTORE_SERVER)
    conn.request('GET', resource)
    logger.debug("store get: %s" % resource)
    r = conn.getresponse()
    status = r.status
    data = r.read()
    logger.debug("store get: %s" % status)
    return status,data
