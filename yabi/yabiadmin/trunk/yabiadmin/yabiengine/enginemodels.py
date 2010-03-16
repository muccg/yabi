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

    # Most of this method is building up the commend line, refactor into its own class,def
    def addJob(self, job_dict):
        logger.debug('')

        tool = Tool.objects.get(name=job_dict["toolName"])

        # TODO Comment why this is needed or delete
        self.save()

        # cache job for later reference
        job_id = job_dict["jobId"] # the id that is used in the json
        self.workflow.job_cache[job_id] = self

        # process the parameterList to get a useful dict
        logger.debug("Process parameterList")
        param_dict = {}
        for toolparam in job_dict["parameterList"]["parameter"]:
            logger.debug('TOOLPARAM:%s'%(toolparam))
            param_dict[toolparam["switchName"]] = self.get_param_value(toolparam)
        
        logger.debug("param_dict = %s"%(param_dict))

        # now build up the command
        command = []
        commandparams = []
        job_stageins = []

        command.append(tool.path)

        for tp in tool.toolparameter_set.order_by('rank').all():

            # check the tool switch against the incoming params
            if tp.switch not in param_dict:
                continue

            # if the switch is the batch on param switch put it in commandparams and add placeholder in command
            if tp == tool.batch_on_param:
                commandparams.extend(param_dict[tp.switch])
                param_dict[tp.switch] = '%' # use place holder now in command


            else:
                # add to job level stagins, later at task level we'll check these and add a stagein if needed
                job_stageins.extend(param_dict[tp.switch])
                
            # run through all the possible switch uses
            switchuse = tp.switch_use.value

            if switchuse == 'switchOnly':
                command.append(tp.switch)

            elif switchuse == 'valueOnly':
                command.append(param_dict[tp.switch][0])

            elif switchuse == 'both':
                command.append("%s %s" % (tp.switch, param_dict[tp.switch][0]))

            elif switchuse == 'combined':
                command.append("%s%s" % (tp.switch, param_dict[tp.switch][0]))

            elif switchuse == 'pair':
                raise Exception('Unimplemented switch type: pair')
        
            elif switchuse == 'none':
                pass

            # TODO else throw

        # add other attributes
        self.command = ' '.join(command)
        logger.debug("JOB PRE PARAMS: %s"%self.commandparams)
        self.commandparams = repr(commandparams) # save string repr of list
        logger.debug("JOB POST PARAMS: %s"%self.commandparams)
        self.job_stageins = repr(job_stageins) # save string repr of list

   
        # TODO HARDCODED
        # set status to complete if null backend
        if tool.backend.name == 'nullbackend':
            self.status = settings.STATUS['complete']
        else:
            self.status = settings.STATUS['pending']

        # TODO this strips outs the per-switch file type extensions
        # add a list of input file extensions as string, we will reconstitute this for use in the wfwrangler
        self.input_filetype_extensions = str(tool.input_filetype_extensions())

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
        if tool.backend.name == 'nullbackend':
            self.stageout = None
        else:
            self.stageout = "%s%s/" % (self.workflow.stageout, "%d - %s"%(self.order+1,tool.display_name) )
        
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

    # TODO used in job.save above, needs to be moved along with the command line code from job.save into its own class/def
    def get_param_value(self, tp):
        logger.debug('')

        logger.debug("======= get_param_value =============: %s" % tp)
    
        value = []
        if type(tp["value"]) == list:
            # parameter input is multiple input files. loop ofer these files
            for item in tp["value"]:

                if type(item) == dict:

                    # handle links to previous nodes
                    if 'type' in item and 'jobId' in item:
                        previous_job = self.workflow.job_cache[item['jobId']]

                        if previous_job.stageout == None:
                            value = eval(previous_job.commandparams)
                        else:
                            value = [u"%s%d/%d/" % (settings.YABI_URL, self.workflow.id, self.workflow.job_cache[item['jobId']].id)]
                        
                    # handle links to previous file selects
                    elif 'type' in item and 'filename' in item and 'root' in item:
                        if item['type'] == 'file':
                            path = ''
                            if item['path']:
                                path = os.path.join(*item['path'])
                                if not path.endswith(os.sep):
                                    path = path + os.sep
                            value.append( '%s%s%s' % (item['root'], path, item['filename']) )
                        elif item['type'] == 'directory':
                            fulluri = item['root']+item['filename']+'/'
                            
                            # get recursive directory listing
                            filelist = backendhelper.get_file_list(self.workflow.user.name, fulluri, recurse=True)
                            
                            logger.debug("FILELIST returned:%s"%str(filelist))
                        
                            value.extend( [ fulluri + X[0] for X in filelist ] )
                
                elif type(item) == str or type(item) == unicode:
                    value.append( item )

        logger.debug("get_param_value() returning: %s"%value)
        return value



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
            job.update_json(data)

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
            
        task.job.update_json(data)
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

