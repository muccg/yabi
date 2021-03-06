# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import os
import datetime
import uuid
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction
from django.db.models import Q
from yabi.yabi.models import BackendCredential, Tool
from yabi.exceptions import InvalidRequestError
from yabi.yabiengine.commandlinetemplate import CommandTemplate
from yabi.yabiengine.models import Workflow, Task, Job, StageIn, Tag
from yabi.yabiengine.engine_logging import create_workflow_logger, create_job_logger
from yabi.yabiengine.urihelper import uriparse, url_join, is_same_location, uriunparse
from six.moves import filter
from yabi import constants as const
import logging

logger = logging.getLogger(__name__)


DEPENDENCIES_EXCLUDED_PATTERNS = [
    r'STDOUT.txt$', r'STDERR.txt$',
    r""" # examples: Y123.e4567 Y123.o4567, Y123.o456.1, Y123.e456-2
    Y\d+        # Y for YABI, followed by some digits (task pk)
    \.          # separated by a dot ...
    [eo]        # from e for stderr, or o for stdout
    \d+         # followed by some digits (remote id)
    ([-.]\d+)?  # and optionally the job array index (separated by - or .)
    $"""
]


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
        if self.status != const.STATUS_ERROR:
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
            "tags": []  # TODO probably can be removed
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

    def _determine_stageout_dir(self, workflow_dict):
        if 'default_stageout' in workflow_dict and workflow_dict['default_stageout']:
            default_stageout = workflow_dict['default_stageout']
        else:
            default_stageout = self.user.default_stageout

        return "%s%s/" % (default_stageout, self.name)

    def create_jobs(self):
        wfl_logger = create_workflow_logger(logger, self.pk)
        logger.debug('----- Creating jobs for workflow id %d -----' % self.pk)

        try:
            with transaction.atomic():
                workflow_dict = json.loads(self.original_json)

                self.stageout = self._determine_stageout_dir(workflow_dict)
                self.save()

                for i, job_dict in enumerate(workflow_dict["jobs"]):
                    job = EngineJob(workflow=self, order=i, start_time=datetime.datetime.now())
                    job.add_job(job_dict)
                wfl_logger.info("Created %d jobs for workflow %d", i, self.pk)

                self.status = const.STATUS_READY
                self.save()
        except Exception:
            wfl_logger.exception("Exception during creating jobs for workflow {0}".format(self.pk))

            self.status = const.STATUS_ERROR
            self.save()

            raise

    def _filter_jobs(self, predicate=lambda x: True, **kwargs):
        qs = EngineJob.objects.filter(workflow=self).order_by("order")
        return list(filter(predicate, qs.filter(**kwargs)))

    def jobs_that_wait_for_dependencies(self):
        return self._filter_jobs(lambda j: j.total_tasks() == 0,
                                 status=const.STATUS_PENDING)

    def jobs_that_need_processing(self):
        def f(j):
            return j.total_tasks() == 0 and not j.has_incomplete_dependencies()
        return self._filter_jobs(f, status=const.STATUS_PENDING)

    def has_jobs_to_process(self):
        return len(self.jobs_that_need_processing()) > 0

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

    def get_job(self, order):
        return EngineJob.objects.get(order=order)


class EngineJob(Job):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        ret = Job.__init__(self, *args, **kwargs)
        if self.command_template:
            try:
                self.template = CommandTemplate()
                self.template.deserialise(self.command_template)
            except ValueError:
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

    def _get_be_cred(self, backend, be_type):
        if backend.is_nullbackend:
            return None
        full_term = Q(credential__user=self.workflow.user) & Q(backend=backend)

        try:
            rval = BackendCredential.objects.get(full_term)
            return rval
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            logger.critical('Invalid %s backend credentials for user: %s and backend: %s' % (be_type, self.workflow.user, self.tool.backend))
            ebcs = BackendCredential.objects.filter(full_term)
            logger.debug("EBCS returned: %s" % ebcs)
            for bc in ebcs:
                logger.debug("%s: Backend: %s Credential: %s" % (bc, bc.credential, bc.backend))
            raise

    @property
    def exec_credential(self):
        return self._get_be_cred(self.tool.backend, 'execution')

    @property
    def fs_credential(self):
        return self._get_be_cred(self.tool.fs_backend, 'FS')

    def update_dependencies(self):
        self.template.update_dependencies(self.workflow, ignored_patterns=DEPENDENCIES_EXCLUDED_PATTERNS)
        return self.template.dependencies

    def has_incomplete_dependencies(self):
        """Check each of the dependencies (previous jobs that must be completed) in the jobs command params.
           The only dependency we have are yabi:// style references in batch_files
        """
        logger.info('Check dependencies for jobid: %s...' % self.id)
        return self.update_dependencies() != 0

    def make_tasks_ready(self):
        for task in EngineTask.objects.filter(job=self):
            # status is a property not an individual model field
            task.status = const.STATUS_READY
            task.save()

    def get_backend_uri(self, credential):
        if credential is None:
            return 'null://%s@localhost.localdomain/' % self.workflow.user.name
        return credential.homedir_uri

    def add_job(self, job_dict):
        assert(job_dict)
        assert(job_dict["toolName"])
        logger.debug(job_dict["toolName"])

        template = CommandTemplate()
        template.setup(self, job_dict)
        template.parse_parameter_description()

        self.job_dict = job_dict
        if "toolId" not in job_dict:
            raise InvalidRequestError("Submitted job %s lacks toolId" % job_dict["toolName"])
        self.tool = Tool.objects.get(id=job_dict["toolId"])
        if not self.tool.enabled:
            raise InvalidRequestError("Can't process workflow with disabled tool '%s'" % self.tool.name)
        if not self.tool.does_user_have_access_to(self.user):
            raise InvalidRequestError("Can't process workflow with inaccessible tool '%s'" % self.tool.name)

        # lets work out the highest copy level supported by this tool and store it in job. This makes no account for the backends capabilities.
        # that will be resolved later when the stagein is created during the walk
        self.preferred_stagein_method = 'link' if self.tool.link_supported else 'lcopy' if self.tool.lcopy_supported else 'copy'

        self.preferred_stageout_method = 'lcopy' if self.tool.lcopy_supported else 'copy'                                                   # stageouts should never be linked. Only local copy or remote copy

        # cache job for later reference
        self.command_template = template.serialise()
        self.command = str(template)                    # text description of command

        self.status = const.STATUS_PENDING
        self.stageout = "%s%s/" % (self.workflow.stageout, "%d - %s" % (self.order + 1, self.tool.get_display_name()))
        self.exec_backend = self.get_backend_uri(self.exec_credential)
        self.fs_backend = self.get_backend_uri(self.fs_credential)
        self.cpus = self.tool.cpus
        self.walltime = self.tool.walltime
        self.module = self.tool.module
        self.queue = self.tool.queue
        self.max_memory = self.tool.max_memory
        self.job_type = self.tool.job_type

        self.save()

    @transaction.atomic
    def create_tasks(self):
        job_logger = create_job_logger(logger, self.pk)
        logger.debug('----- creating tasks for Job %s -----' % self.pk)
        assert self.total_tasks() == 0, "Job already has tasks"

        updated = Job.objects.filter(pk=self.pk, status=const.STATUS_PENDING).update(status=const.JOB_STATUS_PROCESSING)
        if updated == 0:
            job_logger.info("Another process_jobs() must have picked up job %s already" % self.pk)
            return

        self.update_dependencies()

        input_files = self.get_input_files()
        self.create_one_task_for_each_input_file(input_files)

        # there must be at least one task for every job
        if not self.total_tasks():
            job_logger.critical('No tasks for job: %s' % self.pk)
            raise Exception('No tasks for job: %s' % self.pk)

        # mark job as ready so it can be requested by a backend
        self.status = const.STATUS_READY
        self.save()
        self.make_tasks_ready()

        return self.total_tasks()

    def get_input_files(self):
        if self.template.command.is_select_file:
            return []
        input_files = [X for X in self.template.file_sets()]
        return input_files

    def create_one_task_for_each_input_file(self, input_files):
        logger.debug("job %s is having tasks created for %s input files" % (self.pk, len(input_files)))
        if len(input_files) == 0:
            input_files = [None]

        # lets count up our batch_file_list to see how many files there are to process
        # won't count tasks with file == None as these are from not batch param jobs
        count = len(list(filter(lambda x: x is not None, input_files)))
        left_padded_with_zeros = "{0:0>%s}" % len(str(count))

        self.task_total = len(input_files)

        for task_num, input_file in enumerate(input_files, 1):
            task = EngineTask(job=self, status=const.STATUS_PENDING,
                              start_time=datetime.datetime.now(),
                              task_num=task_num)

            task_name = left_padded_with_zeros.format(task_num) if count > 1 else ""
            task.add_task(input_file, task_name)

    def progress_score(self):
        tasks = Task.objects.filter(job=self)
        score = 0.0
        for task in tasks:
            score += task.percent_complete if task.percent_complete is not None else 0.0

        return score

    def total_tasks(self):
        tasknum = float(len(Task.objects.filter(job=self)))
        return tasknum

    def ready_tasks(self):
        return self.task_set.filter(status_requested__isnull=True, status_ready__isnull=False).order_by('id')

    def has_errored_tasks(self):
        return [X.error_msg for X in Task.objects.filter(job=self) if X.status == const.STATUS_ERROR] != []

    def get_errored_tasks_messages(self):
        return [X.error_msg for X in Task.objects.filter(job=self) if X.status == const.STATUS_ERROR]

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
        assert job_dict['jobId'] == job_id + 1  # jobs are 1 indexed in json

        job_dict['status'] = self.status
        job_dict['is_retrying'] = self.is_retrying
        job_dict['tasksComplete'] = float(self.progress_score())
        job_dict['tasksTotal'] = float(self.total_tasks())

        if self.status == const.STATUS_ERROR:
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
        ret = Task.__init__(self, *args, **kwargs)

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
        template.set_uri_conversion(url_join(self.fsbackend_parts.path, self.working_dir, "input") + "/%(filename)s")

        if uridict is None:
            # batchfileless task (eg, select file)
            self.command = template.render()
        else:
            self.command = template.render(uridict)

        self.save()

        # non batch stageins
        for key, stageins in template.all_files():
            logger.debug("key:%s stagein:%s" % (key, stageins))
            for stagein in stageins:
                self.batch_files_stagein(stagein)

        self.status = ''
        self.save()

        logger.info('Created task for job id: %s using command: %s' % (self.job.id, self.command))
        logger.info('working dir is: %s' % (self.working_dir))

    def batch_files_stagein(self, uri):
        self.create_stagein(src=uri, scheme=self.fsscheme,
                            hostname=self.fsbackend_parts.hostname, port=self.fsbackend_parts.port,
                            path=os.path.join(self.fsbackend_parts.path, self.working_dir, "input", uri.rsplit('/')[-1]),
                            username=self.fsbackend_parts.username)

    def create_stagein(self, src, scheme, hostname, port, path, username):
        dst = uriunparse(scheme, hostname, username, path, port)

        # if src and dst are same backend, and the backend supports advanced copy methods, set the method as such
        method = self.determine_stagein_method(src, dst)

        s, created = StageIn.objects.get_or_create(
            task=self,
            src=src,
            dst=dst,
            order=0,
            method=method)

        logger.debug("create_stagein: %s => %s (%s): %s " % (s.src, s.dst, method, "created" if created else "reused"))
        s.save()

    def determine_stagein_method(self, src, dst):
        preferred_stagein_method = self.job.preferred_stagein_method
        if is_same_location(src, dst):
            method = preferred_stagein_method
        else:
            method = 'copy'
        return method
