# -*- coding: utf-8 -*-
import httplib, os
import uuid
from urllib import urlencode
from os.path import splitext
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
from yabiadmin.yabiengine.models import Workflow, Task, Job, StageIn
from yabiadmin.yabiengine.urihelper import uriparse, url_join
from yabiadmin.yabiengine.YabiJobException import YabiJobException

from conf import config

import logging
logger = logging.getLogger('yabiengine')


class EngineWorkflow(Workflow):
    job_cache = {}
    job_dict = []

    class Meta:
        proxy = True

    def walk(self):
        logger.debug('')
        jobset = [X for X in EngineJob.objects.filter(workflow=self).order_by("order")]

        for job in jobset:
            logger.info('Walking job id: %s' % job.id)
            try:

                #check job status
                if not job.status_complete() and not job.status_ready():
                    job.check_dependencies()
                    job.prepare_tasks()
                    job.prepare_job()
                else:
                    logger.info('Job id: %s is %s' % (job.id, job.status))
                    # check all the jobs are complete, if so, changes status on workflow
                    incomplete_jobs = Job.objects.filter(workflow=job.workflow).exclude(status=settings.STATUS['complete'])
                    if not len(incomplete_jobs):
                        job.workflow.status = settings.STATUS['complete']
                        job.workflow.save()

            except YabiJobException,e:
                logger.info("Caught YabiJobException with message: %s" % e)
                continue
            except ObjectDoesNotExist,e:
                logger.critical("ObjectDoesNotExist at wfwrangler.walk: %s" % e)
                import traceback
                logger.debug(traceback.format_exc())
                raise
            except Exception,e:
                logger.critical("Error in workflow wrangler: %s" % e)
                raise
        

class EngineJob(Job):

    tool = None

    class Meta:
        proxy = True

    @property
    def extensions(self):
        '''Reconstitute the input filetype extension list so each create_task can use it'''
        extensions = []
        if self.input_filetype_extensions:
            extensions = (self.input_filetype_extensions)
        return extensions

    
    @property
    def exec_credential(self):
        rval = None

        try:
            rval = BackendCredential.objects.get(credential__user=self.workflow.user, backend=self.tool.backend)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            logger.critical('Invalid filesystem backend credentials for user: %s and backend: %s' % (self.workflow.user, self.tool.backend))
            ebcs = BackendCredential.objects.filter(credential__user=self.workflow.user, backend=self.tool.backend)
            logger.debug("EBCS returned: %s"%(ebcs))
            for bc in ebcs:
                logger.debug("%s: Backend: %s Credential: %s"%(bc,bc.credential,bc.backend))
            raise

        return rval 


    @property
    def fs_credential(self):
        rval = None

        try:
            rval = BackendCredential.objects.get(credential__user=self.workflow.user, backend=self.tool.fs_backend)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            logger.critical('Invalid filesystem backend credentials for user: %s and backend: %s' % (self.workflow.user, self.tool.fs_backend))
            fsbcs = BackendCredential.objects.filter(credential__user=self.workflow.user, backend=self.tool.fs_backend)
            logger.debug("FS Backend Credentials returned: %s"%(fsbcs))
            for bc in fsbcs:
                logger.debug("%s: Backend: %s Credential: %s"%(bc,bc.credential,bc.backend))
            raise

        return rval


    def check_dependencies(self):
        """Check each of the dependencies in the jobs command params.
        Start with a ready value of True and if any of the dependecies are not ready set ready to False.
        """
        logger.debug('')
        logger.info('Check dependencies for jobid: %s...' % self.id)

        logger.debug("++++++++++++++++++++ %s ++++++++++++++++++" % self.batch_files)

        for bfile in eval(self.batch_files):

            if bfile.startswith("yabi://"):
                logger.info('Evaluating bfile: %s' % param)
                scheme, uriparts = uriparse(bfile)
                workflowid, jobid = uriparts.path.strip('/').split('/')
                param_job = Job.objects.get(workflow__id=workflowid, id=jobid)
                if param_job.status != settings.STATUS["complete"]:
                    raise YabiJobException("Job command parameter not complete. Job:%s bfile:%s" % (self.id, bfile))


    # TODO still lots of TODO in this method - mainly moving stuff out of it
    # AH also, should this be a constuctor?
    def addJob(self, job_dict):
        logger.debug('')

        self.job_dict = job_dict
        # AH tool is intrinsic to job, so it would seem to me that this ref is useful,
        # let me know if keep refs to ORM objects like this is not cool
        self.tool = Tool.objects.get(name=job_dict["toolName"])

        # TODO Comment why this is needed or delete
        self.save()

        # cache job for later reference
        job_id = job_dict["jobId"] # the id that is used in the json
        self.workflow.job_cache[job_id] = self

        commandLine = CommandLineHelper(self)

        # add other attributes
        self.command = ' '.join(commandLine.command)
        self.batch_files = commandLine.batch_files # save string repr of list
        self.job_stageins = commandLine.jobstageins # save string repr of list
        self.status = settings.STATUS['pending']

        # TODO this strips outs the per-switch file type extensions
        # add a list of input file extensions as string, we will reconstitute this for use in the wfwrangler
        self.input_filetype_extensions = str(self.tool.input_filetype_extensions_for_batch_param())

        self.stageout = "%s%s/" % (self.workflow.stageout, "%d - %s"%(self.order+1,self.tool.display_name) )
        self.exec_backend = self.exec_credential.homedir_uri
        self.fs_backend = self.fs_credential.homedir_uri
        self.cpus = self.tool.cpus
        self.walltime = self.tool.walltime
        self.module = self.tool.module
        self.queue = self.tool.queue
        self.max_memory = self.tool.max_memory
        self.job_type = self.tool.job_type

        self.save()


    def prepare_tasks(self):
        logger.debug('')
        logger.debug('=================================================== prepare_tasks ===========================================================')
        logger.info('Preparing tasks for jobid: %s...' % self.id)

        tasks_to_create = []

        # get the backend for this job
        # TODO Move this into constructor (addJob should be constructor)
        exec_bc = backendhelper.get_backendcredential_for_uri(self.workflow.user.name, self.exec_backend)
        exec_be = exec_bc.backend
        fs_bc = backendhelper.get_backendcredential_for_uri(self.workflow.user.name, self.fs_backend)
        fs_be = fs_bc.backend
        logger.debug("wfwrangler::prepare_tasks() exec_be:%s exec_bc:%s fs_be:%s fs_bc:%s"%(exec_be,exec_bc,fs_be,fs_bc))

        batch_file_list = eval(self.batch_files)

        if batch_file_list:
            # this creates batch_on_param tasks
            logger.debug("PROCESSING batch on param")
            for bfile in batch_file_list:
                logger.debug("Prepare_task batch file list: %s" % batch_file_list)

                # TODO: fix all this voodoo

                ##################################################
                # handle yabi:// uris
                # fetches the stageout of previous job and
                # adds that to batch_file_list to be processed
                ##################################################
                if bfile.startswith("yabi://"):
                    logger.info('Processing uri %s' % bfile)

                    # parse yabi uri
                    # we may want to look up workflows and jobs on specific servers later,
                    # but just getting path for now as we have just one server
                    scheme, uriparts = uriparse(bfile)
                    workflowid, jobid = uriparts.path.strip('/').split('/')
                    param_job = Job.objects.get(workflow__id=workflowid, id=jobid)

                    # get stage out directory of job
                    stageout = param_job.stageout

                    batch_file_list.append(stageout)


                ##################################################
                # handle yabifs:// uris that are directories
                ##################################################

                # uris ending with a / on the end of the path are directories
                elif bfile.startswith("yabifs://") and param.endswith("/"):
                    logger.info('Processing uri %s' % bfile)

                    logger.debug("PROCESSING")
                    logger.debug("%s -> %s" % (bfile, backendhelper.get_file_list(self.workflow.user.name, bfile)))

                    # get_file_list will return a list of file tuples
                    for f in backendhelper.get_file_list(self.workflow.user.name, bfile):
                        logger.debug("FILELIST %s" % f)
                        tasks_to_create.append([self, bfile, f[0], exec_be, exec_bc, fs_be, fs_bc])


                ##################################################
                # handle yabifs:// uris
                ##################################################
                elif bfile.startswith("yabifs://"):
                    logger.info('Processing uri %s' % bfile)            
                    rest, filename = bfile.rsplit("/",1)
                    tasks_to_create.append([self, rest + "/", filename, exec_be, exec_bc, fs_be, fs_bc])


                ##################################################
                # handle gridftp:// gridftp uris that are directories
                ##################################################

                # uris ending with a / on the end of the path are directories
                elif bfile.startswith("gridftp://") and bfile.endswith("/"):
                    logger.info('Processing uri %s' % bfile)

                    logger.debug("PROCESSING")
                    logger.debug("%s -> %s" % (bfile, backendhelper.get_file_list(self.workflow.user.name, bfile)))

                    # get_file_list will return a list of file tuples
                    for f in backendhelper.get_file_list(self.workflow.user.name, bfile):
                        tasks_to_create.append([self, bfile, f[0], exec_be, exec_bc, fs_be, fs_bc])


                ##################################################
                # handle gridftp:// uris
                ##################################################
                elif bfile.startswith("gridftp://"):
                    logger.info('Processing uri %s' % bfile)            
                    rest, filename = bfile.rsplit("/",1)

                    logger.debug("PROCESSING %s" % bfile)

                    tasks_to_create.append([self, rest + "/", filename, exec_be, exec_bc, fs_be, fs_bc])


                ##################################################
                # handle unknown types
                ##################################################
                else:
                    logger.info('****************************************')
                    logger.info('Unhandled type: ' + bfile)
                    logger.info('****************************************')
                    raise Exception('Unknown file type.')


        else:
            # This creates NON batch on param jobs
            logger.debug("PROCESSING NON batch on param")
            tasks_to_create.append([self, None, None, exec_be, exec_bc, fs_be, fs_bc])


        ##
        ## now loop over these tasks and actually create them
        ##

        num = 1

        # lets count up our batch_file_list to see how many 'real' (as in not yabi://) files there are to process
        # won't count tasks with file == None as these are from not batch param jobs
        count = len([X for X in tasks_to_create if X[2] and X[0].is_task_file_valid(X[2])])

         # lets build a closure that will generate our names for us
        if count>1:
            # the 10 base logarithm will give us how many digits we need to pad
            buildname = lambda n: (n+1,("0"*(int(log10(count))+1)+str(n))[-(int(log10(count))+1):])
        else:
            buildname = lambda n: (n+1, "")

        logger.debug("TASKS TO CREATE: %s" % tasks_to_create)

        # build the first name
        num, name = buildname(num)
        for task_data in tasks_to_create:
            job, file = task_data[0], task_data[2]
            del(task_data[0]) # remove job from task_data as we now are going to call method on job TODO maybe use pop(0) here
            # we should only create a task file if job file is none ie it is a non batch_on_param task
            # or if it is a valid filetype for the batch_on_param
            # TODO REFACTOR - Adam can you look at how this is done
            if file == None or self.is_task_file_valid(file):
                if job.create_task( *(task_data+[name]) ):
                    # task created, bump task
                    num,name = buildname(num)

    def prepare_job(self):
        logger.debug('')
        logger.info('Setting job id %s to ready' % self.id)                
        self.status = settings.STATUS["ready"]
        self.save()
                    
    def is_task_file_valid(self, file):
        """Returns a boolean, true if the file passed in is a valid file for the job. Only uses the file extension to tell."""
        return (splitext(file)[1].strip('.') in self.extensions) or ('*' in self.extensions)



    def create_task(self, param, file, exec_be, exec_bc, fs_be, fs_bc, name=""):
        logger.debug('START TASK CREATION')
        logger.debug("job %s" % self)
        logger.debug("file %s" % file)
        logger.debug("param %s" % param)
        logger.debug("exec_be %s" % exec_be)
        logger.debug("exec_bc %s" % exec_bc)
        logger.debug("fs_be %s" % fs_be)
        logger.debug("fs_bc %s" % fs_bc)

        # TODO param is uri less filename gridftp://amacgregor@xe-ng2.ivec.org/scratch/bi01/amacgregor/
        # rename it to something sensible

        # create the task
        t = EngineTask(job=self, status=settings.STATUS['pending'])
        t.working_dir = str(uuid.uuid4()) # random uuid
        t.name = name
        t.command = self.command
        t.expected_ip = config.config['backend']['port'][0]
        t.expected_port = config.config['backend']['port'][1]
        t.save()

        # basic stuff used by both stagein types
        fsscheme, fsbackend_parts = uriparse(self.fs_backend)
        execscheme, execbackend_parts = uriparse(self.exec_backend)


        ##
        ## JOB STAGEINS
        ##
        ## This section catches all non-batch param files which should appear in job_stageins on job in db
        ##
        ## Take each job stagein
        ## Add a stagein in the database for it
        ## Replace the filename in the command with relative path used in the stagein
        for job_stagein in set(eval(self.job_stageins)): # use set to get unique files
            logger.debug("CREATING JOB STAGEINS")

            if "/" not in job_stagein:
                continue

            dirpath, filename = job_stagein.rsplit("/",1)
            scheme, rest = uriparse(dirpath)

            if scheme not in settings.VALID_SCHEMES:
                continue

            t.command = t.command.replace(job_stagein, url_join(fsbackend_parts.path,t.working_dir, "input", filename))

            t.create_stagein(param=dirpath+'/', file=filename, scheme=fsscheme,
                           hostname=fsbackend_parts.hostname,
                           path=os.path.join(fsbackend_parts.path, t.working_dir, "input", filename),
                           username=fsbackend_parts.username)

            logger.debug('JOB STAGEIN')
            logger.debug("dirpath %s" % dirpath )
            logger.debug("filename %s" % filename)


        ##
        ## BATCH PARAM STAGEINS
        ##
        ## This section catches all batch-param files

        # only make tasks for expected filetypes
        if file and self.is_task_file_valid(file):
            logger.debug("CREATING BATCH PARAM STAGEINS for %s" % file)

            param_scheme, param_uriparts = uriparse(param)
            root, ext = splitext(file)

            # add the task specific file replacing the % in the command line
            t.command = t.command.replace("%", url_join(fsbackend_parts.path,t.working_dir, "input", file))

            t.create_stagein(param=param, file=file, scheme=fsscheme,
                           hostname=fsbackend_parts.hostname,
                           path=os.path.join(fsbackend_parts.path, t.working_dir, "input", file),
                           username=fsbackend_parts.username)



        t.status = settings.STATUS['ready']
        t.save()

        logger.debug('saved========================================')
        logger.info('Creating task for job id: %s using command: %s' % (self.id, t.command))
        logger.info('working dir is: %s' % (t.working_dir) )


        # return true indicates that we actually made a task
        return True 






class EngineTask(Task):

    class Meta:
        proxy = True


    def create_stagein(self, param=None, file=None, scheme=None, hostname=None, path=None, username=None):
        s = StageIn(task=self,
                    src="%s%s" % (param, file),
                    dst="%s://%s@%s%s" % (scheme, username, hostname, path),
                    order=0)

        logger.debug("Stagein: %s <=> %s " % (s.src, s.dst))
        s.save()
        





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

        #TODO Is this the best way to get an engineworkflow rather than a workflow             
        workflow = EngineWorkflow.objects.get(id=task.job.workflow.id)
        workflow.update_json(task.job, data)
        task.job.status = status

        # this save will trigger saves right up to the workflow level
        task.job.save()


        # now double check all the tasks are complete, if so, change status on job
        # and trigger the workflow walk
        incomplete_tasks = Task.objects.filter(job=task.job).exclude(status=settings.STATUS['complete'])
        if not len(incomplete_tasks):
            task.job.status = settings.STATUS['complete']
            task.job.save()
            workflow.walk()

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


