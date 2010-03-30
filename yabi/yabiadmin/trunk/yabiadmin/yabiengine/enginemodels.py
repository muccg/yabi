# -*- coding: utf-8 -*-
import httplib, os, datetime, uuid, traceback
from math import log10
from urllib import urlencode
from os.path import splitext
from conf import config

from psycopg2 import OperationalError

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models, connection, transaction
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

import logging
logger = logging.getLogger('yabiengine')


class EngineWorkflow(Workflow):
    job_cache = {}
    job_dict = []

    class Meta:
        proxy = True

    def build(self):
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
                job.add_job(job_dict)

        except ObjectDoesNotExist, e:
            logger.critical(e)
            logger.critical(traceback.format_exc())        
            raise
        except KeyError, e:
            logger.critical(e)
            logger.critical(traceback.format_exc())        
            raise
        except Exception, e:
            logger.critical(e)
            logger.critical(traceback.format_exc())
            raise

    @transaction.commit_on_success
    def walk(self):
        '''
        Walk through the jobs for this workflow and prepare jobs and tasks,
        check if the workflow has completed after each walk
        '''
        logger.debug('----- Walking workflow id %d -----' % self.id)

        try:
            # TODO ok this is fairly ugly at this point, the code has evolved through bitter experience
            # with things not working rather than from intelligent design. Ideally we should
            # be able to do a much simpler version without the NOWAIT.
            count = 0
            waiting = True
            while (waiting and count < 15):
                count = count + 1
                waiting = False
                try: 
                    cursor = connection.cursor()
                    table = self._meta.db_table
                    logger.debug("Locking table %s" % table)
                    cursor.execute("LOCK TABLE %s IN ACCESS EXCLUSIVE MODE NOWAIT" % table)
                except OperationalError, e:
                    logger.critical(traceback.format_exc())
                    transaction.rollback()
                    waiting = True
                    from time import sleep
                    sleep(count)
                except:
                    logger.critical(traceback.format_exc())
                    raise
            if (count >= 15):
                raise Exception("Timeout waiting for lock on table")

            jobset = [X for X in EngineJob.objects.filter(workflow=self).order_by("order")]
            for job in jobset:
                logger.info('Walking job id: %s' % job.id)

                # dont check complete or ready jobs
                job.update_status()
                job.save()
                if (job.status_complete() or job.status_ready() or job.status_error()):
                    logger.debug("job %s is completed or ready, skipping walk" % job.id)
                    continue

                # we can't proceed until all previous job dependencies are satisfied
                if (job.has_incomplete_dependencies()):
                    logger.info('Incomplete dependencies for job: %s' % job.id)
                    continue

                logger.debug("job %s is is being processed by walk" % job.id) 

                tasks = job.prepare_tasks()
                job.create_tasks(tasks)

                # there must be at least one task for every job
                if not job.task_set.all():
                    logger.critical('No tasks for job: %s' % job.id)
                    job.status = settings.STATUS['error']
                    job.save()
                    continue
            
                # mark job as ready so it can be requested by a backend
                job.status = settings.STATUS["ready"]
                job.save()

                job.make_tasks_ready()               

            # check all the jobs are complete, if so, changes status on workflow
            incomplete_jobs = Job.objects.filter(workflow=self).exclude(status=settings.STATUS['complete'])
            if not len(incomplete_jobs):
                self.status = settings.STATUS['complete']
                self.save()

        except ObjectDoesNotExist,e:
            logger.critical("ObjectDoesNotExist at workflow.walk")
            logger.critical(traceback.format_exc())
            raise
        except Exception,e:
            logger.critical("Error in workflow")
            logger.critical(traceback.format_exc())
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

    @transaction.commit_on_success
    def make_tasks_ready(self): 
        tasks = EngineTask.objects.filter(job=self)
        for task in tasks:
            task.status = settings.STATUS['ready']
            task.save()

    def _walk(self):
        eWorkflow = EngineWorkflow.objects.get(id=self.workflow_id)
        eWorkflow.walk()

    def add_job(self, job_dict):
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
        logger.info('Preparing tasks for jobid: %s...' % self.id)

        if (self.total_tasks() > 0):
            raise Exception("Job already has tasks")

        tasks_to_create = []

        # get the backend for this job
        # TODO Move this into constructor (add_job should be constructor)
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
                    logger.debug("%s -> %s" % (bfile, backendhelper.get_file_list(self.workflow.user.name, bfile)))

                    # get_file_list will return a list of file tuples
                    for f in backendhelper.get_file_list(self.workflow.user.name, bfile):
                        if self.is_task_file_valid(f[0], extension_list):
                            logger.debug("Preparing batch_file task for file %s" % f)
                            tasks_to_create.append([self, bfile, f[0], exec_be, exec_bc, fs_be, fs_bc])

        else:
            # This creates NON batch on param jobs
            logger.debug("prepare_task for a task with no batch_files")
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
            job = task_data[0]
            # remove job from task_data as we now are going to call method on job TODO maybe use pop(0) here
            del(task_data[0]) 
            task = EngineTask(job=job, status=settings.STATUS['pending'])
            task.add_task(*(task_data+[name]))
            num,name = buildname(num)

    def is_task_file_valid(self, file, extensions):
        """Returns a boolean, true if the file passed in is a valid file for the job. Only uses the file extension to tell."""
        logger.debug(file)
        logger.debug(extensions)
        return (splitext(file)[1].strip('.') in extensions) or ('*' in extensions)

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
                'error':0.0,
               
                # TODO Added to allow tasks to be created without a status
                '':0.0
                }[status]
        return score


    def total_tasks(self):
        return float(len(Task.objects.filter(job=self)))


    def has_errored_tasks(self):
        return [X.error_msg for X in Task.objects.filter(job=self) if X.status == settings.STATUS['error']] != []


    def get_errored_tasks_messages(self):
        return [X.error_msg for X in Task.objects.filter(job=self) if X.status == settings.STATUS['error']]


class EngineTask(Task):

    fsscheme = None
    fsbackend_parts = None
    execscheme = None
    execbackend_parts = None

    class Meta:
        proxy = True


    def walk(self):
        if self.status == settings.STATUS['complete']:
            eJob = EngineJob.objects.get(id=self.job_id)
            eJob._walk()

    def add_task(self, uri, batch_file, exec_be, exec_bc, fs_be, fs_bc, name=""):
        logger.debug('')
        logger.debug("batch file %s" % batch_file)
        logger.debug("uri %s" % uri)
        logger.debug("exec_be %s" % exec_be)
        logger.debug("exec_bc %s" % exec_bc)
        logger.debug("fs_be %s" % fs_be)
        logger.debug("fs_bc %s" % fs_bc)

        # uri is uri less filename gridftp://amacgregor@xe-ng2.ivec.org/scratch/bi01/amacgregor/

        # create the task
        self.working_dir = str(uuid.uuid4()) # random uuid
        self.name = name
        self.command = self.job.command
        self.expected_ip = config.config['backend']['port'][0]
        self.expected_port = config.config['backend']['port'][1]
        self.save()

        # basic stuff used by both stagein types
        self.fsscheme, self.fsbackend_parts = uriparse(self.job.fs_backend)
        self.execscheme, self.execbackend_parts = uriparse(self.job.exec_backend)

        self.batch_files_stagein(uri, batch_file)
        self.parameter_files_stagein()

        self.status = ''
        self.save()

        logger.info('Created task for job id: %s using command: %s' % (self.job.id, self.command))
        logger.info('working dir is: %s' % (self.working_dir) )

    def parameter_files_stagein(self):
        ''' 
        All non-batch param files which should appear in job.parameter_files on job in db
       
        Take each job parameter file
        Add a stagein in the database for it
        Replace the filename in the command with relative path used in the stagein
        '''
        for parameter_file_tuple in eval(self.job.parameter_files):
            parameter_file, extension_list = parameter_file_tuple

            # it's one of the non file params
            # TODO please comment why this happens
            if "/" not in parameter_file: 
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
                    yabiusername = uriparts.username
                    filename = backendhelper.get_first_matching_file(self.job.workflow.user.name, stageout, extension_list)
                    if not filename:
                        raise Exception("No matching file found at: %s for %s" % (stageout, extension_list))
                                        
                # append the filename to stageout, then proceed
                parameter_file = "%s%s" % (stageout, filename)
            
            dirpath, filename = parameter_file.rsplit("/",1)
            scheme, rest = uriparse(dirpath)

            if scheme not in settings.VALID_SCHEMES:
                logger.critical('Invalid scheme [%s] in parameter_files, skipping' % scheme)
                continue

            # replace one instance of placeholder for this file
            self.command = self.command.replace('$', url_join(self.fsbackend_parts.path,self.working_dir, "input", filename), 1)

            self.create_stagein(param=dirpath+'/', file=filename, scheme=self.fsscheme,
                           hostname=self.fsbackend_parts.hostname,
                           path=os.path.join(self.fsbackend_parts.path, self.working_dir, "input", filename),
                           username=self.fsbackend_parts.username)

    def batch_files_stagein(self, uri, batch_file):
        ## BATCH PARAM STAGEIN
        if batch_file:
            # add the task specific file replacing the % in the command line
            self.command = self.command.replace("%", url_join(self.fsbackend_parts.path,self.working_dir, "input", batch_file))

            self.create_stagein(param=uri, file=batch_file, scheme=self.fsscheme,
                           hostname=self.fsbackend_parts.hostname,
                           path=os.path.join(self.fsbackend_parts.path, self.working_dir, "input", batch_file),
                           username=self.fsbackend_parts.username)

    def create_stagein(self, param=None, file=None, scheme=None, hostname=None, path=None, username=None):
        s = StageIn(task=self,
                    src="%s%s" % (param, file),
                    dst="%s://%s@%s%s" % (scheme, username, hostname, path),
                    order=0)

        logger.debug("Stagein: %s <=> %s " % (s.src, s.dst))
        s.save()


# Django signals. These are only used to update the store. It should stay this way,
# please refrain from adding anything here other than store updates.

def signal_workflow_post_save(sender, **kwargs):
    logger.debug("workflow post_save signal")
    
    try:
        workflow = kwargs['instance']
        status, data = StoreHelper.updateWorkflow(workflow)
    except Exception, e:
        logger.critical(e)
        logger.critical(traceback.format_exc())
        raise

def signal_job_post_save(sender, **kwargs):
    logger.debug("job post_save signal")

    try:
        job = kwargs['instance']

        # we need an EngineJob so get that from the job.id
        ejob = EngineJob.objects.get(id=job.id)
        score = ejob.progress_score()
        total = ejob.total_tasks()

        # now update the json with the appropriate values
        data = {'tasksComplete':float(score),
                'tasksTotal':float(total)
                }
        if ejob.status == settings.STATUS['error']:
            data['errorMessage'] = str(ejob.get_errored_tasks_messages())
        StoreHelper.updateJob(ejob, data)

    except Exception, e:
        logger.critical(e)
        logger.critical(traceback.format_exc())
        raise
    
# connect up django signals
post_save.connect(signal_workflow_post_save, sender=Workflow)
post_save.connect(signal_job_post_save, sender=Job)

post_save.connect(signal_workflow_post_save, sender=EngineWorkflow)
post_save.connect(signal_job_post_save, sender=EngineJob)
