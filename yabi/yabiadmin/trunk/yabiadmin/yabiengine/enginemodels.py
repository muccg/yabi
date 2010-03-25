# -*- coding: utf-8 -*-
import httplib, os, datetime, uuid
from math import log10
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
from yabiadmin.yabiengine.storehelper import StoreHelper
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
    workflow_dict = None
    
    class Meta:
        proxy = True


    def build(self):
        logger.debug('')
        logger.debug('----- Building workflow id %d -----' % self.id)

        try:
            status, data = StoreHelper.updateWorkflow(self, self.json)

            workflow_dict = json.loads(self.json)

            # sort out the stageout directory
            if 'default_stageout' in workflow_dict and workflow_dict['default_stageout']:
                default_stageout = workflow_dict['default_stageout']
            else:
                default_stageout = self.user.default_stageout

            self.stageout = "%s%s/" % (default_stageout, self.name)
            self.status = settings.STATUS['ready']
            self.save()

            # save the jobs
            for i,job_dict in enumerate(workflow_dict["jobs"]):
                job = EngineJob(workflow=self, order=i, start_time=datetime.datetime.now())
                job.addJob(job_dict)

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


    def walk(self):
        '''
        Walk through the jobs for this workflow and prepare jobs and tasks,
        check if the workflow has completed after each walk
        '''
        logger.debug('')
        logger.debug('----- Walking workflow id %d -----' % self.id)

        try:

            jobset = [X for X in EngineJob.objects.filter(workflow=self).order_by("order")]

            for job in jobset:
                logger.info('Walking job id: %s' % job.id)

                # dont check complete or ready jobs
                if (job.status_complete() or job.status_ready()):
                    continue

                # we can't proceed until all previous job dependencies are satisfied
                if (job.has_incomplete_dependencies()):
                    logger.info('Incomplete dependencies for job: %s' % job.id)
                    continue

                tasks = job.prepare_tasks()
                job.create_tasks(tasks)

                # there must be at least one task for every job
                if not job.task_set.all():
                    job.status = settings.STATUS['error']
                    job.save()
                    continue
                
                job.prepare_job()

            # check all the jobs are complete, if so, changes status on workflow
            incomplete_jobs = Job.objects.filter(workflow=self).exclude(status=settings.STATUS['complete'])
            if not len(incomplete_jobs):
                self.status = settings.STATUS['complete']
                self.save()

        except ObjectDoesNotExist,e:
            logger.critical("ObjectDoesNotExist at workflow.walk: %s" % e)
            import traceback
            logger.debug(traceback.format_exc())
            raise
        except Exception,e:
            logger.critical("Error in workflow: %s" % e)
            import traceback
            logger.debug(traceback.format_exc())
            raise


class EngineJob(Job):

    tool = None

    class Meta:
        proxy = True

    @property
    def extensions(self):
        '''Reconstitute the input filetype extension list so each create_task can use it'''
        extensions = []
        if self.other_files:
            extensions = (self.other_files)
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


    def has_incomplete_dependencies(self):
        """Check each of the dependencies (previous jobs that must be completed) in the jobs command params.
           The only dependency we have are yabi:// style references in batch_files
        """
        rval = False

        logger.info('Check dependencies for jobid: %s...' % self.id)

        for bfile, extension_list in eval(self.batch_files):
            if bfile.startswith("yabi://"):
                logger.info('Evaluating bfile: %s' % bfile)
                scheme, uriparts = uriparse(bfile)
                parts = uriparts.path.strip('/').split('/')
                workflowid, jobid = parts[0], parts[1]
                param_job = Job.objects.get(workflow__id=workflowid, id=jobid)
                if param_job.status != settings.STATUS["complete"]:
                    logger.debug("Job dependencies not complete. Job:%s bfile:%s" % (self.id, bfile))
                    rval = True

        return rval

    # AH also, should this be a constuctor?
    def addJob(self, job_dict):
        logger.debug('')

        self.job_dict = job_dict
        # AH tool is intrinsic to job, so it would seem to me that this ref is useful,
        # let me know if keep refs to ORM objects like this is not cool
        self.tool = Tool.objects.get(name=job_dict["toolName"])

        # cache job for later reference
        job_id = job_dict["jobId"] # the id that is used in the json
        self.workflow.job_cache[job_id] = self

        commandLine = CommandLineHelper(self)

        # add other attributes
        self.command = ' '.join(commandLine.command)
        self.batch_files = commandLine.batch_files # save string repr of list
        self.parameter_files = commandLine.parameter_files # save string repr of list
        self.other_files = commandLine.other_files # save string repr of list
        self.status = settings.STATUS['pending']

        # TODO this strips outs the per-switch file type extensions
        # add a list of input file extensions as string, we will reconstitute this for use in the workflow walk
        self.other_files = str(self.tool.input_filetype_extensions_for_batch_param())

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
        logger.debug("prepare_tasks() exec_be:%s exec_bc:%s fs_be:%s fs_bc:%s"%(exec_be,exec_bc,fs_be,fs_bc))

        batch_file_list = eval(self.batch_files)

        if batch_file_list:

            logger.debug("Prepare_task batch file list: %s" % batch_file_list)

            for batch_file in batch_file_list:

                # this creates batch_on_param tasks
                logger.debug("PROCESSING batch on param")
                logger.debug(batch_file)
                bfile, extension_list = batch_file[0], batch_file[1]


                # handle yabi:// uris
                # fetches the stageout of previous job and
                # adds that to batch_file_list to be processed
                if bfile.startswith("yabi://"):
                    logger.info('Processing uri %s' % bfile)

                    # parse yabi uri
                    # we may want to look up workflows and jobs on specific servers later,
                    # but just getting path for now as we have just one server
                    scheme, uriparts = uriparse(bfile)
                    parts = uriparts.path.strip('/').split('/')
                    workflowid, jobid = parts[0], parts[1]
                    param_job = Job.objects.get(workflow__id=workflowid, id=jobid)

                    # get stage out directory of job
                    stageout = param_job.stageout

                    batch_file_list.append((stageout, extension_list))

                # handle all non yabi:// uris
                else:
                    logger.info('Processing uri %s' % bfile)

                    logger.debug("PROCESSING")
                    logger.debug("%s -> %s" % (bfile, backendhelper.get_file_list(self.workflow.user.name, bfile)))

                    # get_file_list will return a list of file tuples
                    for f in backendhelper.get_file_list(self.workflow.user.name, bfile):
                        logger.debug("FILELIST %s" % f)
                        if self.is_task_file_valid(f[0], extension_list):
                            tasks_to_create.append([self, bfile, f[0], exec_be, exec_bc, fs_be, fs_bc])

        else:
            # This creates NON batch on param jobs
            logger.debug("PROCESSING NON batch on param")
            tasks_to_create.append([self, None, None, exec_be, exec_bc, fs_be, fs_bc])

        return tasks_to_create


    def create_tasks(self, tasks_to_create):
        logger.debug('')

        # lets count up our batch_file_list to see how many 'real' (as in not yabi://) files there are to process
        # won't count tasks with file == None as these are from not batch param jobs
        count = len([X for X in tasks_to_create if X[2]])

         # lets build a closure that will generate our names for us
        if count>1:
            # the 10 base logarithm will give us how many digits we need to pad
            buildname = lambda n: (n+1,("0"*(int(log10(count))+1)+str(n))[-(int(log10(count))+1):])
        else:
            buildname = lambda n: (n+1, "")

        logger.debug("TASKS TO CREATE: %s" % tasks_to_create)

        # build the first name
        num = 1
        num, name = buildname(num)
        for task_data in tasks_to_create:
            job, file = task_data[0], task_data[2]
            del(task_data[0]) # remove job from task_data as we now are going to call method on job TODO maybe use pop(0) here
            # we should only create a task file if job file is none ie it is a non batch_on_param task
            if job.create_task( *(task_data+[name]) ):
                # task created, bump task
                num,name = buildname(num)

    def prepare_job(self):
        logger.debug('')
        logger.info('Setting job id %s to ready' % self.id)                
        self.status = settings.STATUS["ready"]
        self.save()
                    
    def is_task_file_valid(self, file, extensions):
        """Returns a boolean, true if the file passed in is a valid file for the job. Only uses the file extension to tell."""
        logger.debug(file)
        logger.debug(extensions)
        return (splitext(file)[1].strip('.') in extensions) or ('*' in extensions)

    # TODO In haste added the very similar named def 'create_tasks', which might cause confusion
    # Havent looked to closely here yet, but can this move into EngineTask?
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
        ## BATCH PARAM STAGEINS
        ##
        ## This section catches all batch-param files
        if file:
            logger.debug("CREATING BATCH PARAM STAGEINS for %s" % file)

            param_scheme, param_uriparts = uriparse(param)
            root, ext = splitext(file)

            # add the task specific file replacing the % in the command line
            t.command = t.command.replace("%", url_join(fsbackend_parts.path,t.working_dir, "input", file))

            t.create_stagein(param=param, file=file, scheme=fsscheme,
                           hostname=fsbackend_parts.hostname,
                           path=os.path.join(fsbackend_parts.path, t.working_dir, "input", file),
                           username=fsbackend_parts.username)



        ##
        ## PARAMETER STAGEINS
        ##
        ## This section catches all non-batch param files which should appear in parameter_files on job in db
        ##
        ## Take each job parameter file
        ## Add a stagein in the database for it
        ## Replace the filename in the command with relative path used in the stagein
        for parameter_file_tuple in eval(self.parameter_files):
            logger.debug("CREATING JOB STAGEINS")

            parameter_file, extention_list = parameter_file_tuple

            if "/" not in parameter_file: # it's one of the non file params
                continue
            
            # yabi uris
            if parameter_file.startswith('yabi://'):
                yabiuri, filename = parameter_file.rsplit("/",1)
                scheme, uriparts = uriparse(yabiuri)
                parts = uriparts.path.strip('/').split('/')
                workflowid, jobid = parts[0], parts[1]
                prev_job = Job.objects.get(workflow__id=workflowid, id=jobid)

                # get stage out directory of job
                stageout = prev_job.stageout

                if not filename:
                    # we need to get the first file that matches
                    filename = backendhelper.get_first_matching_file(stageout, extension_list)
                    
                # append the filename to stageout, then proceed
                parameter_file = "%s%s" % (stageout, filename)

            
            dirpath, filename = parameter_file.rsplit("/",1)
            scheme, rest = uriparse(dirpath)

            if scheme not in settings.VALID_SCHEMES:
                continue

            # replace one instance of placeholder for this file
            t.command = t.command.replace('$', url_join(fsbackend_parts.path,t.working_dir, "input", filename), 1)

            t.create_stagein(param=dirpath+'/', file=filename, scheme=fsscheme,
                           hostname=fsbackend_parts.hostname,
                           path=os.path.join(fsbackend_parts.path, t.working_dir, "input", filename),
                           username=fsbackend_parts.username)

            logger.debug('JOB PARAMETER FILE')
            logger.debug("dirpath %s" % dirpath )
            logger.debug("filename %s" % filename)


        t.status = settings.STATUS['ready']
        t.save()

        logger.debug('saved========================================')
        logger.info('Creating task for job id: %s using command: %s' % (self.id, t.command))
        logger.info('working dir is: %s' % (t.working_dir) )


        # return true indicates that we actually made a task
        return True 


    def progress_score(self):
        tasks = Task.objects.filter(job=self)
        score=0.0
        for task in tasks:
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
        return score


    def total_tasks(self):
        return float(len(Task.objects.filter(job=self)))


    def has_errored_tasks(self):
        return [X.error_msg for X in Task.objects.filter(job=self) if X.status == settings.STATUS['error']] != []


    def get_errored_tasks_messages(self):
        return [X.error_msg for X in Task.objects.filter(job=self) if X.status == settings.STATUS['error']]



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

def signal_workflow_post_save(sender, **kwargs):
    logger.debug('')
    logger.debug("WORKFLOW post_save signal")
    
    try:
        workflow = kwargs['instance']
        status, data = StoreHelper.updateWorkflow(workflow)
    except Exception, e:
        logger.critical(e)
        raise


def signal_job_post_save(sender, **kwargs):
    logger.debug('')
    job = kwargs['instance']

    try:
        job = kwargs['instance']

        data = {}
        if job.status == settings.STATUS['complete']:
            data = {'tasksComplete':1.0,
                    'tasksTotal':1.0
                    }

        elif job.status == settings.STATUS['error']:
            job.workflow.status = settings.STATUS['error']
            job.workflow.save()

        StoreHelper.updateJob(job, data)

    except Exception, e:
        logger.critical(e)
        raise
    
def signal_task_post_save(sender, **kwargs):
    '''
    Note the different calls to job vs task.job in this method. job refers
    to EngineJob but task.job is a plain job
    '''
    logger.debug('')
    task = kwargs['instance']

    try:
        task.job.update_status()
        task.job.save()

        # we need and EngineJob so get that from the task.job.id
        job = EngineJob.objects.get(id=task.job.id)
        score = job.progress_score()
        total = job.total_tasks()

        # now update the json with the appropriate values
        data = {'tasksComplete':float(score),
                'tasksTotal':float(total)
                }
        if task.job.status == settings.STATUS['error']:
            data['errorMessage'] = str(job.get_errored_tasks_messages())
        StoreHelper.updateJob(job, data)

        if task.job.status == settings.STATUS['complete']:
            # we need to grab an EngineWorkflow from task.job.workflow
            workflow = EngineWorkflow.objects.get(id=task.job.workflow.id)
            workflow.walk()

    except Exception, e:
        logger.critical(e)
        raise


# connect up django signals
post_save.connect(signal_workflow_post_save, sender=Workflow)
post_save.connect(signal_job_post_save, sender=Job)
post_save.connect(signal_task_post_save, sender=Task)


post_save.connect(signal_workflow_post_save, sender=EngineWorkflow)
post_save.connect(signal_job_post_save, sender=EngineJob)
post_save.connect(signal_task_post_save, sender=EngineTask)



