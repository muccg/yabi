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

from django.db.transaction import TransactionManagementError

from yabiadmin.yabi.models import Backend, BackendCredential, Tool, User
from yabiadmin.yabiengine import backendhelper
from yabiadmin.yabiengine import storehelper as StoreHelper
from yabiadmin.yabiengine.commandlinetemplate import CommandTemplate, quote_argument
from yabiadmin.yabiengine.models import Workflow, Task, Job, StageIn, Tag
from yabiadmin.yabiengine.urihelper import uriparse, url_join
from yabiadmin.yabiengine.YabiJobException import YabiJobException

from yabiadmin.yabistoreapp import db

from backendhelper import get_exec_backendcredential_for_uri

import logging
logger = logging.getLogger(__name__)

from yabiadmin.constants import *
from yabiadmin.yabistoreapp import db

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

    def errored_during_create_jobs(self):
        if self.status != STATUS_ERROR:
            return False
        # if the Workflow status is error and we have less jobs than we received in the JSON
        # it means we couldn't create jobs from the request -> we had an error during create_jobs()
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
        if self.errored_during_create_jobs():
            # We have to do this to allow the FE to reuse the Workflow
            # If create_jobs() failed there would be no jobs
            d['jobs'] = json.loads(self.original_json)['jobs']
        else:
            for job in self.get_jobs():
                jobs.append(job.as_dict())
            d['jobs'] = jobs
        return d

    def get_jobs(self):
        return EngineJob.objects.filter(workflow=self).order_by("order")

    @transaction.commit_on_success
    def create_jobs(self):
        logger.debug('----- Creating jobs for workflow id %d -----' % self.id)

        try:
            workflow_dict = json.loads(self.original_json)

            # sort out the stageout directory
            if 'default_stageout' in workflow_dict and workflow_dict['default_stageout']:
                default_stageout = workflow_dict['default_stageout']
            else:
                default_stageout = self.user.default_stageout

            self.stageout = "%s%s/" % (default_stageout, self.name)
            self.save()

            # save the jobs
            for i,job_dict in enumerate(workflow_dict["jobs"]):
                job = EngineJob(workflow=self, order=i, start_time=datetime.datetime.now())
                job.add_job(job_dict)

            self.status = STATUS_READY
            self.save()

        except Exception, e:
            transaction.rollback()
            logger.exception("Exception during creating jobs for workflow {0}".format(self.pk))

            self.status = STATUS_ERROR
            self.save()
            transaction.commit()

            raise

    def jobs_that_need_processing(self):
        return [j for j in EngineJob.objects.filter(workflow=self).order_by("order") if j.total_tasks() == 0 and not j.has_incomplete_dependencies() and j.status == STATUS_PENDING]

    def has_jobs_to_process(self):
        return (len(self.jobs_that_need_processing()) > 0)

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
            logger.critical('Invalid filesystem backend credentials for user: %s and backend: %s' % (self.workflow.user, self.tool.fs_backend))
            fsbcs = BackendCredential.objects.filter(credential__user=self.workflow.user, backend=self.tool.fs_backend)
            logger.debug("FS Backend Credentials returned: %s"%(fsbcs))
            for bc in fsbcs:
                logger.debug("%s: Backend: %s Credential: %s"%(bc,bc.credential,bc.backend))
            raise

        return rval

    def update_dependencies(self):
        self.template.update_dependencies(self.workflow, ignore_glob_list=FNMATCH_EXCLUDE_GLOBS)
        return self.template.dependencies

    def has_incomplete_dependencies(self):
        """Check each of the dependencies (previous jobs that must be completed) in the jobs command params.
           The only dependency we have are yabi:// style references in batch_files
        """
        logger.info('Check dependencies for jobid: %s...' % self.id)
        return self.update_dependencies() != 0

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
        #self.preferred_stagein_method = 'link' if self.tool.link_supported else 'lcopy' if self.tool.lcopy_supported else 'copy'
        self.preferred_stagein_method = 'copy'

        self.preferred_stageout_method = 'copy'
        #self.preferred_stageout_method = 'lcopy' if self.tool.lcopy_supported else 'copy'                                                   # stageouts should never be linked. Only local copy or remote copy

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


    @transaction.commit_on_success
    def create_tasks(self):
        logger.debug('----- creating tasks for Job %s -----' % self.pk)
        assert self.total_tasks() == 0, "Job already has tasks"


        updated = Job.objects.filter(pk=self.pk, status=STATUS_PENDING).update(status=JOB_STATUS_PROCESSING)
        if updated == 0:
            logger.info("Another process_jobs() must have picked up job %s already" % self.pk)
            return

        try:
            self.update_dependencies()
            be = get_exec_backendcredential_for_uri(self.workflow.user.name, self.exec_backend)

            input_files = self.get_input_files()
            self.create_one_task_for_each_input_file(input_files, be)

            # there must be at least one task for every job
            if not self.total_tasks():
                logger.critical('No tasks for job: %s' % self.pk)
                self.status = STATUS_ERROR
                self.workflow.status = STATUS_ERROR
                self.save()
                self.workflow.save()
                transaction.commit()
                raise Exception('No tasks for job: %s' % self.pk)

            # mark job as ready so it can be requested by a backend
            self.status = STATUS_READY
            self.save()
            self.make_tasks_ready()

            return self.total_tasks()

        except:
            transaction.rollback()
            # We couldn't sucessfully create tasks for the job so we will set
            # the status to PENDING (ie. allowing a retry to pick it up again)
            self.status = STATUS_PENDING
            self.save()
            transaction.commit()
            raise

    def get_input_files(self):
        if self.template.command.is_select_file:
            return []
        input_files = [X for X in self.template.file_sets()]
        return input_files


    def create_one_task_for_each_input_file(self, input_files, be):
        logger.debug("job %s is having tasks created for %s input files" % (self.pk, len(input_files)))
        assert is_managed() == True
        if len(input_files) == 0:
            input_files = [None]

        # lets count up our batch_file_list to see how many files there are to process
        # won't count tasks with file == None as these are from not batch param jobs
        count = len(filter(lambda x: x is not None, input_files))
        left_padded_with_zeros = "{0:0>%s}" % len(str(count))

        self.task_total = len(input_files)

        for task_num, input_file in enumerate(input_files):
            task = EngineTask(job=self, status=STATUS_PENDING, start_time=datetime.datetime.now(), execution_backend_credential=be, task_num=task_num+1)

            task_name = left_padded_with_zeros.format(task_num+1) if count > 1 else ""
            task.add_task(input_file, task_name)


    def progress_score(self):
        tasks = Task.objects.filter(job=self)
        score=0.0
        for task in tasks:
            score += task.percent_complete if task.percent_complete is not None else 0.0

        return score


    def total_tasks(self):
        tasknum = float(len(Task.objects.filter(job=self)))
        return tasknum

    def ready_tasks(self):
        return self.task_set.filter(status_requested__isnull=True, status_ready__isnull=False).order_by('id')

    def has_errored_tasks(self):
        return [X.error_msg for X in Task.objects.filter(job=self) if X.status == STATUS_ERROR] != []


    def get_errored_tasks_messages(self):
        return [X.error_msg for X in Task.objects.filter(job=self) if X.status == STATUS_ERROR]

    def as_dict(self):
        # TODO This will have to be able to generate the full JSON
        # In this step of the refactoring it will just get it's json from the workflow
        # UPDATE CW - the following json.loads line is failing with unwalked workflows. Refactoring needs to be completed
        # HACK CW - short circuit the function so front end can get a response rather than an error.
        if not self.workflow.original_json:
            return {}
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

    def __init__(self, *args, **kwargs):
        ret = Task.__init__(self,*args, **kwargs)

        # basic stuff used by both stagein types
        self.fsscheme, self.fsbackend_parts = uriparse(self.job.fs_backend)
        self.execscheme, self.execbackend_parts = uriparse(self.job.exec_backend)

        return ret

    @property
    def stageout(self):
        return self.job.stageout + ("" if self.job.stageout.endswith("/") else "/") + ("" if not self.name else self.name + "/")

    def get_stageins(self):
        return StageIn.objects.filter(task=self).order_by('order')

    @property
    def workflow_id(self):
        return self.job.workflow.id

    def add_task(self, uridict, name=""):
        logger.debug("add_task called with uridict: %s, name: %s" % (uridict, name))

        # create the task
        self.working_dir = str(uuid.uuid4())
        self.name = name

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
            logger.debug("key:%s stagein:%s" % (key,stageins))
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

        method = 'copy' # temporary fix
        s, created = StageIn.objects.get_or_create(task=self,
                    src=src,
                    dst=dst,
                    order=0,
                    method=method)

        logger.debug("create_stagein: %s => %s (%s): %s " % (s.src, s.dst, method, "created" if created else "reused"))
        s.save()


    def cascade_status(self):
       job_old_status = self.job.status
       job_cur_status = self.job.update_status()

       if job_cur_status != job_old_status and job_cur_status in (STATUS_ERROR, STATUS_COMPLETE, STATUS_ABORTED):
           self.job.workflow.update_status()

       return (job_cur_status != job_old_status)

