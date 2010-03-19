# -*- coding: utf-8 -*-
import httplib, os
from urllib import urlencode

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import simplejson as json, webhelpers
from django.db.models.signals import post_save
from django.utils.webhelpers import url

from yabiadmin.yabmin.models import Backend, BackendCredential, Tool, User
from yabiadmin.yabiengine import backendhelper
from yabiadmin.yabiengine.commandlinehelper import CommandLineHelper
from yabiadmin.yabiengine.models import Workflow, Task, Job
from yabiadmin.yabiengine.urihelper import uriparse, url_join


import logging
logger = logging.getLogger('yabiengine')


class EngineWorkflow(Workflow):
    job_cache = {}

    class Meta:
        proxy = True
        

class EngineJob(Job):

    class Meta:
        proxy = True

    # TODO
    # Most of this method is building up the commend line, refactor into its own class,def
    def addJob(self, job_dict):
        logger.debug('')

        tool = Tool.objects.get(name=job_dict["toolName"])

        # TODO Comment why this is needed or delete
        self.save()

        # cache job for later reference
        job_id = job_dict["jobId"] # the id that is used in the json
        self.workflow.job_cache[job_id] = self

        commandLine = CommandLineHelper(self, job_dict, self.workflow.job_cache)

        # add other attributes
        self.command = ' '.join(commandLine.command)
        self.commandparams = commandLine.commandparams # save string repr of list
        self.job_stageins = commandLine.jobstageins # save string repr of list
   
        # TODO HARDCODED
        # if we need a null backend, then we should create one that just marks any jobs it gets as completed
        # set status to complete if null backend
        if tool.backend.name == 'nullbackend':
            self.status = settings.STATUS['complete']
        else:
            self.status = settings.STATUS['pending']

        # TODO this strips outs the per-switch file type extensions
        # add a list of input file extensions as string, we will reconstitute this for use in the wfwrangler
        self.input_filetype_extensions = str(tool.input_filetype_extensions_for_batch_param())

        try:
            exec_backendcredential = BackendCredential.objects.get(credential__user=self.workflow.user, backend=tool.backend)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            logger.critical('Invalid filesystem backend credentials for user: %s and backend: %s' % (self.workflow.user, tool.backend))
            ebcs = BackendCredential.objects.filter(credential__user=self.workflow.user, backend=tool.backend)
            logger.debug("EBCS returned: %s"%(ebcs))
            for bc in ebcs:
                logger.debug("%s: Backend: %s Credential: %s"%(bc,bc.credential,bc.backend))
            raise


        try:
            fs_backendcredential = BackendCredential.objects.get(credential__user=self.workflow.user, backend=tool.fs_backend)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            # TODO this was broiken (syntax errors) and does not currently log anything
            logger.critical('Invalid filesystem backend credentials for user: %s and backend: %s' % (self.workflow.user, tool.fs_backend))
            fsbcs = BackendCredential.objects.filter(credential__user=self.workflow.user, backend=tool.fs_backend)
            logger.debug("FS Backend Credentials returned: %s"%(fsbcs))
            for bc in fsbcs:
                logger.debug("%s: Backend: %s Credential: %s"%(bc,bc.credential,bc.backend))
            raise


        #TODO hardcoded
        # See above, we should delete this nullbackend specific stuff, does it matter if it has a stageout dir?
        if tool.backend.name == 'nullbackend':
            self.stageout = None
        else:
            self.stageout = "%s%s/" % (self.workflow.stageout, "%d - %s"%(self.order+1,tool.display_name) )
       
            # TODO delete this, make it a job for the backends
            # make that directory
            backendhelper.mkdir(self.workflow.user.name, self.stageout)

        self.exec_backend = exec_backendcredential.homedir_uri
        self.fs_backend = fs_backendcredential.homedir_uri
        self.cpus = tool.cpus
        self.walltime = tool.walltime
        self.module = tool.module
        self.queue = tool.queue
        self.max_memory = tool.max_memory
        self.job_type = tool.job_type

        self.save()



class EngineTask(Task):

    class Meta:
        proxy = True


# Django signals

def yabistore_update(resource, data):
    logger.debug('')
    data = urlencode(data)
    headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
    conn = httplib.HTTPConnection(settings.YABISTORE_SERVER)
    conn.request('POST', resource, data, headers)
    logger.debug("YABISTORE POST:")
    logger.debug(settings.YABISTORE_SERVER)
    logger.debug(resource)
    logger.debug(data)

    r = conn.getresponse()
    
    status = r.status
    data = r.read()
    assert status == 200    
    logger.debug("result:")
    logger.debug(status)
    logger.debug(data)
    
    return status,data


def workflow_save(sender, **kwargs):
    logger.debug('')
    workflow = kwargs['instance']
    
    logger.debug("WORKFLOW SAVE")
    logger.debug(workflow)

    try:
        # update the yabistore
        if kwargs['created']:
            resource = os.path.join(settings.YABISTORE_BASE,"workflows", workflow.user.name)
        else:
            resource = os.path.join(settings.YABISTORE_BASE,"workflows", workflow.user.name, str(workflow.yabistore_id))

        data = {'json':workflow.json,
                'name':workflow.name,
                'status':workflow.status
                }

        logger.debug("workflow_save::yabistoreupdate")
        logger.debug(resource)
        logger.debug(data)
        
        status, data = yabistore_update(resource, data)

        logger.debug("STATUS: %s" % status)
        logger.debug("DATA: %s" % data)
        
        # if this was created. save the returned id into yabistore_id
        if kwargs['created']:
            logger.debug("SAVING WFID")
            assert status==200
            workflow.yabistore_id = int(data)
            workflow.save()
        
    except Exception, e:
        logger.critical(e)
        raise


def job_save(sender, **kwargs):
    logger.debug('')
    job = kwargs['instance']

    try:

        if job.status == settings.STATUS['complete']:
            data = {'tasksComplete':1.0,
                    'tasksTotal':1.0
                    }
            job.workflow.update_json(job, data)

        elif job.status == settings.STATUS['error']:
            job.workflow.status = settings.STATUS['error']
            job.workflow.save()

    except Exception, e:
        logger.critical(e)
        raise

    
def task_save(sender, **kwargs):
    logger.debug('')
    task = kwargs['instance']


    # TODO this code that works out how many tasks are done
    # should move to job model
    # TODO REFACTOR move to job perhaps
    try:
        # get all the tasks for this job
        jobtasks = Task.objects.filter(job=task.job)
        running = False
        error = False
        score=0.0
        for task in jobtasks:
            status = task.status
            score += { 
                'pending':0.0,
                'ready':0.0,
                'requested':0.01,
                'stagein':0.05,
                'mkdir':0.1,
                'exec':0.11,
                'exec:unsubmitted':0.12,
                'exec:pending':0.13,
                'exec:active':0.2,
                'exec:cleanup':0.7,
                'exec:done':0.75,
                'exec:error':0.0,
                'stageout':0.8,
                'cleaning':0.9,
                'complete':1.0,
                'error':0.0
                }[status]

        total = float(len(jobtasks))

        if status != settings.STATUS['ready'] and status != settings.STATUS['requested']:
            running = True

        if status == settings.STATUS['error']:
            error = True

        # work out if this job is in an error state
        errored = [X.error_msg for X in jobtasks if X.status == settings.STATUS['error']]

        status = None
        if error:
            status = settings.STATUS['error']
        elif score == total:
            status = settings.STATUS['complete']
        elif running:
            status = settings.STATUS['running']
        else:
            status = settings.STATUS['pending']

        errorMessage = None if not error else errored[0]

        if error:
            logger.debug("ERROR! message = %s" % errorMessage)

            # if there are errors, and the relative job has a status that isn't 'error'
            if task.job.status != settings.STATUS['error']:
                # set the job to error
                task.job.status = settings.STATUS['error']


        # now update the json with the appropriate values
        data = {'tasksComplete':float(score),
                'tasksTotal':float(total)
                }
        if errorMessage:
            data['errorMessage'] = errorMessage
            
        task.job.workflow.update_json(task.job, data)
        task.job.status = status

        # this save will trigger saves right up to the workflow level
        task.job.save()


        # now double check all the tasks are complete, if so, change status on job
        # and trigger the workflow walk
        incomplete_tasks = Task.objects.filter(job=task.job).exclude(status=settings.STATUS['complete'])
        if not len(incomplete_tasks):
            task.job.status = settings.STATUS['complete']
            task.job.save()
            wfwrangler.walk(task.job.workflow)

        # double check for error status
        # set the job status to error
        error_tasks = Task.objects.filter(job=task.job, status=settings.STATUS['error'])
        if error_tasks:
            task.job.status = settings.STATUS['error']
            task.job.save()

    except Exception, e:
        logger.critical(e)
        raise



# connect up django signals
post_save.connect(workflow_save, sender=Workflow)
post_save.connect(task_save, sender=Task)
post_save.connect(job_save, sender=Job)

post_save.connect(workflow_save, sender=EngineWorkflow)
post_save.connect(task_save, sender=EngineTask)
post_save.connect(job_save, sender=EngineJob)

# must import this here to avoid circular reference
from yabiengine import wfwrangler

