# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###

import httplib, os, datetime, uuid, traceback
from math import log10
from urllib import urlencode
from os.path import splitext
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models, connection, transaction
from django.db.models import Q
from django.db.transaction import enter_transaction_management, leave_transaction_management, managed, is_dirty, is_managed
from django.conf import settings
from django.utils import simplejson as json
from ccg.utils import webhelpers
from ccg.utils.webhelpers import url
from yabiadmin.utils import detect_rdbms

from django.db.transaction import TransactionManagementError

from yabiadmin.yabi.models import Backend, BackendCredential, Tool, User
from yabiadmin.yabiengine import backendhelper 
from yabiadmin.yabiengine import storehelper as StoreHelper
from yabiadmin.yabiengine.commandlinetemplate import CommandTemplate, quote_argument
from yabiadmin.yabiengine.models import Workflow, Task, Job, StageIn, Tag
from yabiadmin.yabiengine.urihelper import uriparse, url_join
from yabiadmin.yabiengine.YabiJobException import YabiJobException

from yabiadmin.yabistoreapp import db

import logging
logger = logging.getLogger(__name__)

from constants import *
from yabistoreapp import db

FNMATCH_EXCLUDE_GLOBS = [ '*/STDOUT.txt', '*/STDERR.txt', 'STDOUT.txt', 'STDERR.txt' ]

class EngineWorkflow(Workflow):
    job_cache = {}
    job_dict = []

    class Meta:
        proxy = True
        verbose_name = 'workflow'
        verbose_name_plural = 'workflows'

    @property
    def workflow_id(self):
        return self.id

    @property 
    def json(self): 
        return json.dumps(self.as_dict()) 
 
    def errored_in_build(self):
        if self.status != STATUS_ERROR:
            return False
        # if the Workflow status is error and we have less jobs than we received in the JSON
        # it means we couldn't build() all jobs from the request -> we had an error during build()
        received_json = json.loads(self.original_json)
        if 'jobs' not in received_json:
            return False
        received_jobs_count = len(received_json['jobs'])
        return (received_jobs_count > self.job_set.count())

    def as_dict(self): 
        d = { 
                "name": self.name, 
                "tags": [] # TODO probably can be removed 
            }  
        jobs = [] 
        if self.errored_in_build():
            # We have to do this to allow the FE to reuse the Workflow
            # If build() failed there would be no jobs
            d['jobs'] = json.loads(self.original_json)['jobs']
        else: 
            for job in self.get_jobs(): 
                jobs.append(job.as_dict()) 
            d['jobs'] = jobs 
        return d 

    def get_jobs(self):
        return EngineJob.objects.filter(workflow=self).order_by("order") 

    @transaction.commit_on_success
    def build(self):
        logger.debug('----- Building workflow id %d -----' % self.id)

        try:
            workflow_dict = json.loads(self.original_json)
            
            # sort out the stageout directory
            if 'default_stageout' in workflow_dict and workflow_dict['default_stageout']:
                default_stageout = workflow_dict['default_stageout']
            else:
                default_stageout = self.user.default_stageout

            self.stageout = "%s%s/" % (default_stageout, self.name)
            self.status = STATUS_READY
            self.save()

            # save the jobs
            for i,job_dict in enumerate(workflow_dict["jobs"]):
                job = EngineJob(workflow=self, order=i, start_time=datetime.datetime.now())
                job.add_job(job_dict)

        except Exception, e:
            transaction.rollback()

            self.status = STATUS_ERROR
            self.save()
            transaction.commit()

            logger.critical(e)
            logger.critical(traceback.format_exc())

            raise
    
    def jobs_that_need_walking(self):
        return [j for j in EngineJob.objects.filter(workflow=self).order_by("order") if j.total_tasks() == 0 and not j.has_incomplete_dependencies()]

    def needs_walking(self):
        return (len(self.jobs_that_need_walking()) > 0)

    @transaction.commit_manually
    def walk(self):
        '''
        Walk through the jobs for this workflow and prepare jobs and tasks,
        check if the workflow has completed after each walk
        '''
        logger.debug('----- Walking workflow id %d -----' % self.id)
        
        try:
            jobset = [X for X in EngineJob.objects.filter(workflow=self).order_by("order")]
            for job in jobset:
                logger.debug('----- Walking workflow id %d job id %d -----' % (self.id, job.id))

                # dont walk job if it already has tasks
                if job.total_tasks() > 0:
                    logger.info("job %s has tasks, skipping walk" % job.id)
                    continue

                # we can't proceed until all previous job dependencies are satisfied
                if job.has_incomplete_dependencies():
                    logger.info('job %s has incomplete dependencies, skipping walk' % job.id)
                    continue

                # This will open up a new transaction for creating all the tasks of a Job
                # TODO TSZ - it might make sense to change all this code to walk jobs instead
                # Walking one job (ie. creating tasks for it) seems to be the unit of work here
                job.create_tasks()

                # there must be at least one task for every job
                if not job.total_tasks():
                    logger.critical('No tasks for job: %s' % job.id)
                    job.status = STATUS_ERROR
                    self.status = STATUS_ERROR
                    job.save()
                    self.save()
                    transaction.commit()
                    continue
            
                # mark job as ready so it can be requested by a backend
                job.status = STATUS_READY
                job.save()

                job.make_tasks_ready()          
                transaction.commit()

            # Making sure the transactions opened in the loop are closed
            # ex. job.total_tasks() opens a transaction, then it could exit the loop with continue    
            transaction.commit()

        except Exception,e:
            transaction.rollback()

            self.status = STATUS_ERROR
            self.save()
            transaction.commit()

            logger.critical("Exception raised in workflow::walk")
            logger.critical(traceback.format_exc())

            raise

    def change_tags(self, taglist):
        current_tags = [wft.tag.value for wft in self.workflowtag_set.all()]
        new_tags = [t for t in taglist if t not in current_tags]

        # insert new tags
        for new_tag in new_tags:
            try:
                tag = Tag.objects.get(value=new_tag)
            except Tag.DoesNotExist:
                tag = Tag.objects.create(value=new_tag)
            self.workflowtag_set.create(tag=tag)

        # delete old tags
        for wft in self.workflowtag_set.exclude(tag__value__in=taglist):
            wft.delete()
            if not wft.tag.workflowtag_set.exists():
                wft.tag.delete()

    def get_jobs(self):
        return EngineJob.objects.filter(workflow=self).order_by("order")

    def get_job(self, order):
        return EngineJob.objects.get(order=order)


class EngineJob(Job):

    tool = None

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        ret = Job.__init__(self,*args, **kwargs)
        if self.command_template:
            try:
                self.template = CommandTemplate()
                self.template.deserialise(self.command_template)
            except ValueError, e: 
                logger.warning("Unable to deserialise command_template on engine job id: %s" % self.id)

        else:
            self.template = None
        return ret

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
            print 'Invalid filesystem backend credentials for user: %s and backend: %s' % (self.workflow.user, self.tool.fs_backend)
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
        logger.info('Check dependencies for jobid: %s...' % self.id)
        self.template.update_dependencies(self.workflow, ignore_glob_list=FNMATCH_EXCLUDE_GLOBS)
        return self.template.dependencies!=0

    def make_tasks_ready(self): 
        tasks = EngineTask.objects.filter(job=self)
        for task in tasks:
            task.status = STATUS_READY
            task.save()

    def add_job(self, job_dict):
        assert(job_dict)
        assert(job_dict["toolName"])
        logger.debug(job_dict["toolName"])
        
        template = CommandTemplate()
        template.setup(self, job_dict)
        template.parse_parameter_description()
        
        self.job_dict = job_dict
        # AH tool is intrinsic to job, so it would seem to me that this ref is useful,
        # let me know if keep refs to ORM objects like this is not cool
        self.tool = Tool.objects.get(name=job_dict["toolName"])

        # lets work out the highest copy level supported by this tool and store it in job. This makes no account for the backends capabilities.
        # that will be resolved later when the stagein is created during the walk
        self.preferred_stagein_method = 'link' if self.tool.link_supported else 'lcopy' if self.tool.lcopy_supported else 'copy'
        self.preferred_stageout_method = 'lcopy' if self.tool.lcopy_supported else 'copy'                                                   # stageouts should never be linked. Only local copy or remote copy
        
        # cache job for later reference
        job_id = job_dict["jobId"] # the id that is used in the json
        self.command_template = template.serialise()
        self.command = str(template)                    # text description of command
        
        self.status = STATUS_PENDING
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

    def create_tasks(self):
        tasks = self._prepare_tasks()
        #print "_prepare_tasks returned: %s"%(str(tasks))
        
        # by default Django is running with an open transaction
        transaction.commit()

        # see http://code.djangoproject.com/svn/django/trunk/django/db/transaction.py
        assert is_dirty() == False
        
        try:
            enter_transaction_management()
            managed(True)

            assert is_managed() == True

            from django.db import connection
            cursor = connection.cursor()
            logger.debug("Acquiring lock on %s for job %s" % (Task._meta.db_table, self.id))
            rdbms = detect_rdbms()
            if rdbms == 'postgres':
                cursor.execute('LOCK TABLE %s IN ACCESS EXCLUSIVE MODE' % Task._meta.db_table)
            elif rdbms == 'mysql':
                cursor.execute('LOCK TABLES %s WRITE, %s WRITE' % (Task._meta.db_table, StageIn._meta.db_table))
            elif rdbms == 'sqlite':
                # don't do anything!
                pass
            else:
                assert("Locking code not implemented for db backend %s " % settings.DATABASES['default']['ENGINE'])

            if (self.total_tasks() == 0):
                logger.debug("job %s is having tasks created" % self.id) 
                self._create_tasks(tasks)
            else:
                logger.debug("job %s has tasks, skipping create_tasks" % self.id)

            if (settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql'):
                cursor.execute('UNLOCK TABLES')
            transaction.commit()
            logger.debug('Committed, released lock')
        except:
            logger.critical(traceback.format_exc())
            transaction.rollback()
            logger.debug('Rollback, released lock')
            raise
        finally:
            leave_transaction_management()
            assert is_dirty() == False

    def _prepare_tasks(self):
        logger.info('Preparing tasks for jobid: %s...' % self.id)

        if (self.total_tasks() > 0):
            raise Exception("Job already has tasks")

        tasks_to_create = []

        if self.template.command.is_select_file or not len([X for X in self.template.file_sets()]):
            return [ [self,None ] ]
        else:
            for input_file_set in self.template.file_sets():
                tasks_to_create.append([self, input_file_set])    

        return tasks_to_create

    def _create_tasks(self, tasks_to_create):
        logger.debug("creating tasks: %s" % tasks_to_create)
        assert is_managed() == True

        # lets count up our batch_file_list to see how many files there are to process
        # won't count tasks with file == None as these are from not batch param jobs
        
        count = len([X for X in tasks_to_create if X[1]])
        
         # lets build a closure that will generate our names for us
        if count>1:
            # the 10 base logarithm will give us how many digits we need to pad
            buildname = lambda n: (n+1,("0"*(int(log10(count))+1)+str(n))[-(int(log10(count))+1):])
        else:
            buildname = lambda n: (n+1, "")
       
        # build the first name
        num = 1
        num, name = buildname(num)
        for task_data in tasks_to_create:
            job = task_data[0]
            # remove job from task_data as we now are going to call method on job TODO maybe use pop(0) here
            del(task_data[0]) 
            task = EngineTask(job=job, status=STATUS_PENDING, start_time=datetime.datetime.now())
            #print "ADD TASK: %s"%(str(task_data+[name]))
            task.add_task(*(task_data+[name]))
            num,name = buildname(num)

        
    def progress_score(self):
        tasks = Task.objects.filter(job=self)
        score=0.0
        for task in tasks:
            score += task.percent_complete if task.percent_complete is not None else 0.0

        return score


    def total_tasks(self):
        tasknum = float(len(Task.objects.filter(job=self)))
        return tasknum


    def has_errored_tasks(self):
        return [X.error_msg for X in Task.objects.filter(job=self) if X.status == STATUS_ERROR] != []


    def get_errored_tasks_messages(self):
        return [X.error_msg for X in Task.objects.filter(job=self) if X.status == STATUS_ERROR]

    def as_dict(self):
        # TODO This will have to be able to generate the full JSON
        # In this step of the refactoring it will just get it's json from the workflow
        workflow_dict = json.loads(self.workflow.original_json)
        job_id = int(self.order)
        job_dict = workflow_dict['jobs'][job_id]
        assert job_dict['jobId'] == job_id + 1 # jobs are 1 indexed in json

        job_dict['status'] = self.status
        job_dict['tasksComplete'] = float(self.progress_score())
        job_dict['tasksTotal'] = float(self.total_tasks())

        if self.status == STATUS_ERROR:
            job_dict['errorMessage'] = str(self.get_errored_tasks_messages())

        if self.stageout:
            job_dict['stageout'] = self.stageout
        return job_dict


class EngineTask(Task):

    fsscheme = None
    fsbackend_parts = None
    execscheme = None
    execbackend_parts = None

    class Meta:
        proxy = True

    @property
    def workflow_id(self):
        return self.job.workflow.id

    def add_task(self, uridict, name=""):
        logger.debug("uridict: %s" % (uridict))
        
        # create the task
        self.working_dir = str(uuid.uuid4()) # random uuid
        self.name = name
        
        # basic stuff used by both stagein types
        self.fsscheme, self.fsbackend_parts = uriparse(self.job.fs_backend)
        self.execscheme, self.execbackend_parts = uriparse(self.job.exec_backend)

        # make the command from the command template
        template = self.job.template
        
        # set our template batch uri conversion path
        template.set_uri_conversion(url_join(self.fsbackend_parts.path, self.working_dir, "input")+"/%(filename)s")
        
        if uridict is None:
            # batchfileless task (eg, select file)
            self.command = template.render()
        else:
            self.command = template.render(uridict)
        
        self.tasktag = settings.TASKTAG
        self.save()

        # non batch stageins
        for key,stageins in template.all_files():
            print "key:%s stagein:%s"%(key,stageins)
            for stagein in stageins:
                self.batch_files_stagein(stagein)

        self.status = ''
        self.save()
        
        logger.info('Created task for job id: %s using command: %s' % (self.job.id, self.command))
        logger.info('working dir is: %s' % (self.working_dir) )

    def batch_files_stagein(self, uri):
        self.create_stagein(src=uri, scheme=self.fsscheme,
                           hostname=self.fsbackend_parts.hostname, port=self.fsbackend_parts.port,
                           path=os.path.join(self.fsbackend_parts.path, self.working_dir, "input", uri.rsplit('/')[-1]),
                           username=self.fsbackend_parts.username)

    def create_stagein(self, src, scheme, hostname, port, path, username):
        preferred_stagein_method = self.job.preferred_stagein_method
        
        if port:
            dst = "%s://%s@%s:%d%s" % (scheme, username, hostname, port, path)
        else:
            dst = "%s://%s@%s%s" % (scheme, username, hostname, path)
        
        # if src and dst are same backend, and the backend supports advanced copy methods, set the method as such
        sscheme,srest = uriparse(src)
        dscheme,drest = uriparse(dst)
        if sscheme==dscheme and srest.hostname==drest.hostname and srest.port==drest.port:
            method = preferred_stagein_method
        else:
            method = 'copy'
        
        s, created = StageIn.objects.get_or_create(task=self,
                    src=src,
                    dst=dst,
                    order=0,
                    method=method)

        logger.debug("Stagein: %s <=> %s (%s): %s " % (s.src, s.dst, method, "created" if created else "reused"))
        s.save()

