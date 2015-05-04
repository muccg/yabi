# -*- coding: utf-8 -*-
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
# -*- coding: utf-8 -*-
import json
import os
from django.db import models
from yabi.yabi.models import User, Backend, Tool
from yabi.yabiengine import backendhelper
from ccg_django_utils import webhelpers
from ccg_django_utils.webhelpers import url
from yabi.yabiengine.urihelper import uriparse, url_join
from datetime import datetime
from six.moves import filter
from yabi.constants import *
import logging

logger = logging.getLogger(__name__)


STAGING_COPY_CHOICES = (
    ('copy', 'remote copy'),
    ('lcopy', 'local copy'),
    ('link', 'symbolic link')
)


class Status(object):
    COLOURS = {
        STATUS_PENDING: 'grey',
        STATUS_READY: 'orange',
        STATUS_REQUESTED: 'orange',
        STATUS_RUNNING: 'orange',
        STATUS_COMPLETE: 'green',
        STATUS_ERROR: 'red'
    }

    def get_status_colour(self, status):
        return self.COLOURS.get(status, 'grey')


class Editable(object):
    @models.permalink
    def edit_url(self):
        admin_str = 'admin:%s_%s_change' % (self._meta.app_label, self._meta.object_name.lower())
        return (admin_str, (self.id,))

    def edit_link(self):
        return '<a href="%s">Edit</a>' % self.edit_url()
    edit_link.short_description = 'Edit'
    edit_link.allow_tags = True


class SavedWorkflow(models.Model, Editable):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    json = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        get_latest_by = "created_on"


class Workflow(models.Model, Editable, Status):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    last_modified_on = models.DateTimeField(null=True, auto_now=True, editable=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    status = models.TextField(max_length=64, blank=True)
    abort_requested_by = models.ForeignKey(User, related_name='aborted_workflows', null=True)
    abort_requested_on = models.DateTimeField(null=True)
    stageout = models.CharField(max_length=1000)
    shared = models.BooleanField(default=False)
    original_json = models.TextField()

    class Meta:
        get_latest_by = "created_on"

    def __unicode__(self):
        return self.name

    @property
    def workflowid(self):
        return self.id

    @models.permalink
    def summary_url(self):
        return ('workflow_summary', (), {'workflow_id': self.id})

    def delete_cascade(self):
        tags = [t.tag for t in self.workflowtag_set.all()]
        self.delete()
        for tag in filter(lambda t: not t.workflowtag_set.exists(), tags):
            tag.delete()

    def get_jobs_queryset(self):
        """return a query set of jobs in order"""
        return self.job_set.order_by('order')

    def get_jobs(self):
        return self.get_jobs_queryset().all()

    def get_job(self, order):
        return self.job_set.get(order=order)

    def update_status(self):
        FINISHED = (STATUS_COMPLETE, STATUS_ERROR, STATUS_ABORTED)

        job_statuses = [x['status'] for x in Job.objects.filter(workflow=self).values('status')]
        jobs_finished = [status in FINISHED for status in job_statuses]
        jobs_errored = [STATUS_ERROR == status for status in job_statuses]

        if not all(jobs_finished):
            if any(jobs_errored):
                self.status = STATUS_ERROR
                self.save()
            # Handles transition from READY to RUNNING
            # TODO Could be clearer than this
            elif self.status == STATUS_READY:
                if any([status in (STATUS_RUNNING, STATUS_COMPLETE) for status in job_statuses]):
                    self.status = STATUS_RUNNING
                    self.save()
            return self.status

        # All jobs should be finished (either completed, errored or aborted) at this point
        if STATUS_ABORTED in job_statuses:
            status = STATUS_ABORTED
        elif STATUS_ERROR in job_statuses:
            status = STATUS_ERROR
        else:
            assert all([status == STATUS_COMPLETE for status in job_statuses]), "All jobs should be completed"
            status = STATUS_COMPLETE

        self.status = status
        self.end_time = datetime.now()
        self.save()

        return self.status

    def get_status_colour(self):
        return Status.COLOURS.get(self.status, 'grey')

    @property
    def is_finished(self):
        return (self.status in TERMINATED_STATUSES and
                all([j.status in TERMINATED_STATUSES for j in self.job_set.all()]))

    @property
    def colour(self):
        return self.get_status_colour()

    @property
    def is_aborting(self):
        return (self.abort_requested_on is not None)

    @property
    def is_aborted(self):
        return (self.status == STATUS_ABORTED)

    @property
    def is_retrying(self):
        return any([j.is_retrying for j in self.job_set.all()])

    @property
    def highest_retry_count(self):
        return max([0] + [t.retry_count for t in Task.objects.filter(job__workflow__pk=self.pk)])

    def share(self):
        self.shared = True
        self.save()


class Tag(models.Model):
    value = models.CharField(max_length=255)


class WorkflowTag(models.Model):
    workflow = models.ForeignKey(Workflow)
    tag = models.ForeignKey(Tag)


class Job(models.Model, Editable, Status):
    workflow = models.ForeignKey(Workflow)
    order = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    tool = models.ForeignKey(Tool, null=True)
    cpus = models.CharField(max_length=64, null=True, blank=True)
    walltime = models.CharField(max_length=64, null=True, blank=True)
    module = models.TextField(null=True, blank=True)
    queue = models.CharField(max_length=50, default='normal', null=True, blank=True)
    max_memory = models.CharField(max_length=64, null=True, blank=True)
    job_type = models.CharField(max_length=40, default='single', null=True, blank=True)
    status = models.CharField(max_length=64, blank=True)
    exec_backend = models.CharField(max_length=256)
    fs_backend = models.CharField(max_length=256)
    task_total = models.IntegerField(null=True, blank=True)

    command = models.TextField()                # store here a string representation of the template
    # Base64 encoded TODO change to BinaryField when moving to Django 1.6+
    command_template = models.TextField(null=True, blank=True)               # store here the serialised version of the template.

    # TODO: delete these columns from the DB table
    # batch_files = models.TextField(blank=True, null=True)
    # parameter_files = models.TextField(blank=True, null=True)
    # other_files = models.TextField(blank=True, null=True)

    stageout = models.CharField(max_length=1000, null=True)
    preferred_stagein_method = models.CharField(max_length=5, null=False, choices=STAGING_COPY_CHOICES)
    preferred_stageout_method = models.CharField(max_length=5, null=False, choices=STAGING_COPY_CHOICES)

    dynamic_backends = models.ManyToManyField('DynamicBackendInstance', through='JobDynamicBackend', null=True, blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.workflow.name, self.order)

    def status_ready(self):
        return self.status == STATUS_READY

    def status_complete(self):
        return self.status == STATUS_COMPLETE

    def status_error(self):
        return self.status == STATUS_ERROR

    def get_status_colour(self):
        return Status.COLOURS.get(self.status, 'grey')

    @property
    def colour(self):
        return self.get_status_colour()

    @property
    def workflowid(self):
        return self.workflow.id

    @property
    def user(self):
        return self.workflow.user

    def update_status(self):
        '''
        Checks all the tasks for a job and sets the job status based on precedence of the task status.
        The order of the list being checked is therefore important.
        '''
        for status in [STATUS_ERROR, STATUS_EXEC_ERROR, 'pending', 'requested', 'stagein', 'mkdir', 'exec', 'exec:active', 'exec:pending', 'exec:unsubmitted', 'exec:running', 'exec:cleanup', 'exec:done', 'stageout', 'cleaning', STATUS_BLOCKED, STATUS_READY, STATUS_COMPLETE, STATUS_ABORTED]:
            if [T for T in Task.objects.filter(job=self) if T.status == status]:
                # we need to map the task status values to valid job status values
                if status == STATUS_EXEC_ERROR:
                    self.status = STATUS_ERROR
                elif status.startswith('exec') or status in ['stageout', 'cleaning', 'stagein', 'mkdir']:
                    self.status = STATUS_RUNNING
                else:
                    self.status = status

                if status == STATUS_COMPLETE:
                    if [T for T in Task.objects.filter(job=self) if T.status == STATUS_ABORTED]:
                        # at least one aborted the rest completed
                        status = STATUS_ABORTED
                    else:
                        self.end_time = datetime.now()

                assert(self.status in STATUS)
                self.save()
                break

        return self.status

    @property
    def is_finished(self):
        '''Returns True if all the Tasks of the Job finished.
        Status could be COMPLETED, ABORTED or ERROR.'''
        return all(map(lambda t: t.is_finished, Task.objects.filter(job=self)))

    @property
    def is_workflow_aborting(self):
        return self.workflow.is_aborting

    @property
    def is_retrying(self):
        return any([t.is_retrying for t in self.task_set.all()])

    @property
    def has_dynamic_backend(self):
        if self.tool is None or self.tool.fs_backend is None:
            return False
        return (self.tool.fs_backend.dynamic_backend or
                self.tool.backend.dynamic_backend)


class Task(models.Model, Editable, Status):
    job = models.ForeignKey(Job)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    job_identifier = models.TextField(blank=True)
    command = models.TextField(blank=True)
    error_msg = models.CharField(max_length=1000, null=True, blank=True)
    is_retrying = models.BooleanField(default=False)
    retry_count = models.IntegerField(default=0)
    task_num = models.IntegerField(null=True, blank=True)

    # new status boolean like fields:
    # these are set to the date and time of when the status is changed to this value.
    # this is to decouple the status updates in time
    # if null then the task has never held this status
    status_pending = models.DateTimeField(null=True, blank=True)
    status_ready = models.DateTimeField(null=True, blank=True)
    status_requested = models.DateTimeField(null=True, blank=True)
    status_stagein = models.DateTimeField(null=True, blank=True)
    status_mkdir = models.DateTimeField(null=True, blank=True)
    status_exec = models.DateTimeField(null=True, blank=True)
    status_exec_unsubmitted = models.DateTimeField(null=True, blank=True)
    status_exec_pending = models.DateTimeField(null=True, blank=True)
    status_exec_active = models.DateTimeField(null=True, blank=True)
    status_exec_running = models.DateTimeField(null=True, blank=True)
    status_exec_cleanup = models.DateTimeField(null=True, blank=True)
    status_exec_done = models.DateTimeField(null=True, blank=True)
    status_exec_error = models.DateTimeField(null=True, blank=True)
    status_stageout = models.DateTimeField(null=True, blank=True)
    status_cleaning = models.DateTimeField(null=True, blank=True)
    status_complete = models.DateTimeField(null=True, blank=True)
    status_error = models.DateTimeField(null=True, blank=True)
    status_aborted = models.DateTimeField(null=True, blank=True)
    status_blocked = models.DateTimeField(null=True, blank=True)

    percent_complete = models.FloatField(blank=True, null=True)                     # This is between 0.0 and 1.0. if we are null, then the task has not begun at all
    remote_id = models.CharField(max_length=256, blank=True, null=True)             # when the backend actually starts the task, this will be set to the task id
    remote_info = models.CharField(max_length=2048, blank=True, null=True)          # this will contain json describing the remote task information

    working_dir = models.CharField(max_length=256, null=True, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)                  # if we are null, we behave the old way and use our task.id

    envvars_json = models.TextField(blank=True)

    def json(self):
        # formulate our status url and our error url
        # use the yabi embedded in this server
        statusurl = webhelpers.url("/engine/status/task/%d" % self.id)
        syslogurl = webhelpers.url("/engine/syslog/task/%d" % self.id)
        remoteidurl = webhelpers.url("/engine/remote_id/%d" % self.id)
        remoteinfourl = webhelpers.url("/engine/remote_info/%d" % self.id)

        # get our tools fs_backend
        fsscheme, fsbackend_parts = uriparse(self.job.fs_backend)
        logger.debug("getting fs backend for user: %s fs_backend:%s" % (self.job.workflow.user.name, self.job.fs_backend))
        fs_backend = backendhelper.get_fs_backend_for_uri(self.job.workflow.user.name, self.job.fs_backend)
        logger.debug("fs backend is: %s" % fs_backend)

        # get out exec backend so we can get our submission script
        logger.debug("getting exec backendcredential for user: %s exec_backend:%s" % (self.job.workflow.user.name, self.job.exec_backend))
        submission_backendcredential = backendhelper.get_exec_backendcredential_for_uri(self.job.workflow.user.name, self.job.exec_backend)
        logger.debug("exec backendcredential is: %s" % (submission_backendcredential))

        submission_backend = submission_backendcredential.backend

        submission = submission_backendcredential.submission if str(submission_backend.submission).isspace() else submission_backend.submission

        # if the tools filesystem and the users stageout area are on the same schema/host/port
        # then use the preferred_copy_method, else default to 'copy'
        so_backend = backendhelper.get_fs_backend_for_uri(self.job.workflow.user.name, self.job.stageout)
        soscheme, sobackend_parts = uriparse(self.job.stageout)
        if so_backend == fs_backend and soscheme == fsscheme and sobackend_parts.hostname == fsbackend_parts.hostname and sobackend_parts.port == fsbackend_parts.port and sobackend_parts.username == fsbackend_parts.username:
            stageout_method = self.job.preferred_stageout_method
        else:
            stageout_method = "copy"

        output = {
            "yabiusername": self.job.workflow.user.name,
            "taskid": self.id,
            "statusurl": statusurl,
            "syslogurl": syslogurl,
            "remoteidurl": remoteidurl,
            "remoteinfourl": remoteinfourl,
            "stagein": [],
            "exec": {
                "command": self.command,
                "backend": url_join(self.job.exec_backend),
                "fsbackend": url_join(self.job.fs_backend, self.working_dir),
                "workingdir": os.path.join(fsbackend_parts.path, self.working_dir),
                "cpus": self.job.cpus,
                "walltime": self.job.walltime,
                "module": self.job.module,
                "queue": self.job.queue,
                "memory": self.job.max_memory,
                "jobtype": self.job.job_type,
                "tasknum": self.task_num,
                "tasktotal": self.job.task_total,
                "submission": submission
            },
            "stageout": self.job.stageout + ("" if self.job.stageout.endswith("/") else "/") + ("" if not self.name else self.name + "/"),
            "stageout_method": stageout_method
        }

        for s in self.stagein_set.all():
            src_scheme, src_rest = uriparse(s.src)
            dst_scheme, dst_rest = uriparse(s.dst)

            # method may be 'copy', 'lcopy' or 'link'
            output["stagein"].append({"src": s.src, "dst": s.dst,
                                      "order": s.order, "method": s.method})

        return json.dumps(output)

    def __unicode__(self):
        return self.job.workflow.name

    @property
    def workflowid(self):
        return self.job.workflow.id

    @property
    def user(self):
        return self.job.user

    @staticmethod
    def status_attr(status):
        return "status_" + status.replace(':', '_')

    def set_status(self, status):
        # set the requested status to 'now'
        varname = self.status_attr(status)
        setattr(self, varname, datetime.now())

        if status != STATUS_BLOCKED and status != STATUS_RESUME:
            self.percent_complete = STATUS_PROGRESS_MAP[status]

        if status == STATUS_COMPLETE:
            self.end_time = datetime.now()

    def get_status(self):
        for status in STATUSES_REVERSE_ORDER:
            varname = self.status_attr(status)
            if getattr(self, varname):
                return status
        return ''

    # status is a property that sets or gets the present status
    status = property(get_status, set_status)

    def link_to_json(self):
        return '<a href="%s%d">%s</a>' % (url('/engine/task_json/'), self.id, "JSON")
    link_to_json.allow_tags = True
    link_to_json.short_description = "JSON"

    def link_to_syslog(self):
        return '<a href="%s?table_name=task&table_id=%d">%s</a>' % (url('/admin-pane/yabiengine/syslog/'), self.id, "Syslog")
    link_to_syslog.allow_tags = True
    link_to_syslog.short_description = "Syslog"

    def get_status_colour(self):
        return Status.COLOURS.get(self.status, 'grey')

    @property
    def colour(self):
        return self.get_status_colour()

    @property
    def is_workflow_aborting(self):
        return self.job.workflow.is_aborting

    @property
    def envvars(self):
        if self.envvars_json is None or self.envvars_json.strip() == '':
            return {}
        return json.loads(self.envvars_json)

    @property
    def is_finished(self):
        return self.status in TERMINATED_STATUSES

    def mark_task_as_retrying(self, message="Some error occurred"):
        self.is_retrying = True
        self.error_msg = message
        self.save()

    def finished_retrying(self):
        self.is_retrying = False
        self.error_msg = None
        self.save()


class DynamicBackendInstance(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    created_for_job = models.ForeignKey(Job)
    configuration = models.TextField()
    instance_handle = models.CharField(max_length=256)
    hostname = models.CharField(max_length=512, blank=True)
    destroyed_on = models.DateTimeField(blank=True, null=True)


class JobDynamicBackend(models.Model):
    BE_TYPE_CHOICES = (
        ('fs', 'filesystem'),
        ('ex', 'execution'),
    )
    BE_TYPE_MAP = dict(BE_TYPE_CHOICES)
    BE_TYPE_REVERSED_MAP = dict(map(reversed, BE_TYPE_CHOICES))

    @staticmethod
    def descr_to_type(descr):
        return JobDynamicBackend.BE_TYPE_REVERSED_MAP[descr]

    job = models.ForeignKey(Job)
    backend = models.ForeignKey(Backend)
    instance = models.ForeignKey(DynamicBackendInstance)
    be_type = models.CharField(max_length=2, choices=BE_TYPE_CHOICES)

    @property
    def type_descr(self):
        return self.BE_TYPE_MAP[self.be_type]


class StageIn(models.Model, Editable):
    src = models.CharField(max_length=256)
    dst = models.CharField(max_length=256)
    order = models.IntegerField()
    task = models.ForeignKey(Task)
    method = models.CharField(max_length=5, choices=STAGING_COPY_CHOICES)

    @property
    def workflowid(self):
        return self.task.job.workflow.id

    def matches_filename(self, filename):
        _, parts = uriparse(self.src)
        return filename == os.path.basename(parts.path)


class QueueBase(models.Model):
    class Meta:
        abstract = True

    workflow = models.ForeignKey(Workflow)
    created_on = models.DateTimeField(auto_now_add=True)

    def name(self):
        return self.workflow.name

    def user_name(self):
        return self.workflow.user.name


class QueuedWorkflow(QueueBase):
    pass


class Syslog(models.Model):
    message = models.TextField(blank=True)
    table_name = models.CharField(max_length=64, null=True)
    table_id = models.IntegerField(null=True)
    created_on = models.DateTimeField(null=True, auto_now=True, editable=False)

    def __unicode__(self):
        return self.message

    def json(self):
        return json.dumps({'table_name': self.table_name,
                           'table_id': self.table_id,
                           'message': self.message})
