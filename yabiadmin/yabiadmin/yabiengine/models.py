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
# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.conf import settings
from yabiadmin.yabi.models import User
from yabiadmin.yabiengine import backendhelper
from yabiadmin.yabiengine.urihelper import uriparse
from django.utils import simplejson as json
from ccg.utils import webhelpers
from ccg.utils.webhelpers import url
import httplib, os
from yabiadmin.yabiengine.urihelper import uriparse, url_join
from urllib import urlencode
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

from constants import *

STAGING_COPY_CHOICES = (
    ( 'copy',   'remote copy' ),
    ( 'lcopy',  'local copy' ),
    ( 'link',   'symbolic link' )
)

class Status(object):
    COLOURS = {
        STATUS_PENDING:  'grey',
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

class Workflow(models.Model, Editable, Status):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    last_modified_on = models.DateTimeField(null=True, auto_now=True, editable=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    status = models.TextField(max_length=64, blank=True)
    stageout = models.CharField(max_length=1000)
    original_json = models.TextField()

    def __unicode__(self):
        return self.name

    @property
    def workflowid(self):
        return self.id

    @models.permalink
    def summary_url(self):
        return ('workflow_summary', (), {'workflow_id': self.id})

    def summary_link(self):
        return '<a href="%s">Summary</a>' % self.summary_url()

    summary_link.short_description = 'Summary'
    summary_link.allow_tags = True

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
        job_statuses = [x['status'] for x in Job.objects.filter(workflow=self).values('status')]
        if STATUS_ERROR in job_statuses:
            self.status = STATUS_ERROR
            self.end_time = datetime.now()
            self.save()
            return
        if len(filter(lambda s: s != STATUS_COMPLETE, job_statuses)) == 0:
            self.status = STATUS_COMPLETE
            self.end_time = datetime.now()
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
    cpus = models.CharField(max_length=64, null=True, blank=True)
    walltime = models.CharField(max_length=64, null=True, blank=True)
    module = models.TextField(null=True, blank=True)
    queue = models.CharField(max_length=50, default='normal', null=True, blank=True)
    max_memory = models.CharField(max_length=64, null=True, blank=True)
    job_type = models.CharField(max_length=40, default='single', null=True, blank=True)
    status = models.CharField(max_length=64, blank=True)
    exec_backend = models.CharField(max_length=256)
    fs_backend = models.CharField(max_length=256)
    
    command = models.TextField()                # store here a string representation of the template
    command_template = models.TextField(null=True, blank=True)               # store here the serialised version of the template
    
    # TODO: delete these columns from the DB table
    #batch_files = models.TextField(blank=True, null=True)
    #parameter_files = models.TextField(blank=True, null=True)
    #other_files = models.TextField(blank=True, null=True)
    
    stageout = models.CharField(max_length=1000, null=True)
    preferred_stagein_method = models.CharField(max_length=5, null=False, choices=STAGING_COPY_CHOICES)
    preferred_stageout_method = models.CharField(max_length=5, null=False, choices=STAGING_COPY_CHOICES)


    def __unicode__(self):
        return "%s - %s" % (self.workflow.name, self.order)

    def status_ready(self):
        return self.status == STATUS_READY

    def status_complete(self):
        return self.status == STATUS_COMPLETE

    def status_error(self):
        return self.status == STATUS_ERROR

    @property
    def workflowid(self):
        return self.workflow.id

    def update_status(self):
        '''
        Checks all the tasks for a job and sets the job status based on precedence of the task status.
        The order of the list being checked is therefore important.
        '''
        cur_status = self.status
        for status in [STATUS_ERROR, 'exec:error', 'pending', 'requested', 'stagein', 'mkdir', 'exec', 'exec:active', 'exec:pending', 'exec:unsubmitted', 'exec:running', 'exec:cleanup', 'exec:done', 'stageout', 'cleaning', STATUS_BLOCKED, STATUS_READY, STATUS_COMPLETE]:
            if Task.objects.filter(job=self, status=status):
                # we need to map the task status values to valid job status values
                if status == 'exec:error':
                    self.status = STATUS_ERROR
                elif status.startswith('exec') or status in ['stageout', 'cleaning', 'stagein', 'mkdir']:
                    self.status = STATUS_RUNNING
                else:
                    self.status = status

                # fill end_time if finished
                if status == STATUS_COMPLETE:
                    self.end_time = datetime.now()
                
                assert(self.status in STATUS)
                self.save()
                break
        if self.status != cur_status and self.status in (STATUS_ERROR, STATUS_COMPLETE):
            self.workflow.update_status()

class Task(models.Model, Editable, Status):
    job = models.ForeignKey(Job)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    job_identifier = models.TextField(blank=True)
    command = models.TextField(blank=True)
    exec_backend = models.CharField(max_length=256, blank=True)
    fs_backend = models.CharField(max_length=256, blank=True)
    error_msg = models.CharField(max_length=1000, null=True, blank=True)

    status = models.CharField(max_length=64, blank=True)
    percent_complete = models.FloatField(blank=True, null=True)                     # This is between 0.0 and 1.0. if we are null, then the task has not begun at all
    remote_id = models.CharField(max_length=256, blank=True, null=True)             # when the backend actually starts the task, this will be set to the task id
    remote_info = models.CharField(max_length=2048, blank=True, null=True)          # this will contain json describing the remote task information

    working_dir = models.CharField(max_length=256, null=True, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)                  # if we are null, we behave the old way and use our task.id
    tasktag = models.CharField(max_length=256, null=True, blank=True)           # if we are null, we behave the old way and use our task.id

    def json(self):
        # formulate our status url and our error url
        # use the yabiadmin embedded in this server
        statusurl = webhelpers.url("/engine/status/task/%d" % self.id)
        errorurl = webhelpers.url("/engine/error/task/%d" % self.id)
        remoteidurl = webhelpers.url("/engine/remote_id/%d" % self.id)
        remoteinfourl = webhelpers.url("/engine/remote_info/%d" % self.id)

        # get our tools fs_backend
        fsscheme, fsbackend_parts = uriparse(self.job.fs_backend)
        logger.debug("getting fs backend for user: %s fs_backend:%s"%(self.job.workflow.user.name,self.job.fs_backend))
        fs_backend = backendhelper.get_fs_backend_for_uri(self.job.workflow.user.name,self.job.fs_backend)
        logger.debug("fs backend is: %s"%(fs_backend))
        
        # get out exec backend so we can get our submission script
        logger.debug("getting exec backendcredential for user: %s exec_backend:%s"%(self.job.workflow.user.name,self.job.exec_backend))
        submission_backendcredential = backendhelper.get_exec_backendcredential_for_uri(self.job.workflow.user.name,self.job.exec_backend)
        logger.debug("exec backendcredential is: %s"%(submission_backendcredential))
        
        submission_backend = submission_backendcredential.backend
        
        submission = submission_backendcredential.submission if str(submission_backend.submission).isspace() else submission_backend.submission
        
        # if the tools filesystem and the users stageout area are on the same schema/host/port
        # then use the preferred_copy_method, else default to 'copy'
        so_backend = backendhelper.get_fs_backend_for_uri(self.job.workflow.user.name,self.job.stageout)
        soscheme, sobackend_parts = uriparse(self.job.stageout)
        if  so_backend==fs_backend and soscheme==fsscheme and sobackend_parts.hostname==fsbackend_parts.hostname and sobackend_parts.port==fsbackend_parts.port and sobackend_parts.username==fsbackend_parts.username:
            stageout_method = self.job.preferred_stageout_method
        else:
            stageout_method = "copy"
        
        output = {
            "yabiusername":self.job.workflow.user.name,
            "taskid":self.id,
            "statusurl":statusurl,
            "errorurl":errorurl,
            "remoteidurl":remoteidurl,
            "remoteinfourl":remoteinfourl,
            "stagein":[],
            "exec":{
                "command":self.command,
                "backend": url_join(self.job.exec_backend),
                "fsbackend": url_join(self.job.fs_backend, self.working_dir),
                "workingdir": os.path.join(fsbackend_parts.path,self.working_dir),
                "cpus": self.job.cpus,
                "walltime": self.job.walltime,
                "module": self.job.module,
                "queue": self.job.queue,
                "memory":self.job.max_memory,
                "jobtype":self.job.job_type,
                "submission":submission
                
                },
            "stageout":self.job.stageout+("" if self.job.stageout.endswith("/") else "/")+("" if not self.name else self.name+"/"),
            "stageout_method":stageout_method
            }

        
        stageins = self.stagein_set.all()
        for s in stageins:
            src_backend = backendhelper.get_fs_backend_for_uri(self.job.workflow.user.name,s.src)
            src_scheme, src_rest = uriparse(s.src)
            dst_backend = backendhelper.get_fs_backend_for_uri(self.job.workflow.user.name,s.dst)
            dst_scheme, dst_rest = uriparse(s.dst)
            
            output["stagein"].append({"src":s.src, "dst":s.dst, "order":s.order, "method":s.method})              # method may be 'copy', 'lcopy' or 'link'

        return json.dumps(output)

    def __unicode__(self):
        return self.job.workflow.name

    @property
    def workflowid(self):
        return self.job.workflow.id

    def link_to_json(self):
        return '<a href="%s%d">%s</a>' % (url('/engine/task_json/'), self.id, "JSON")
    link_to_json.allow_tags = True
    link_to_json.short_description = "JSON"

    def link_to_syslog(self):
        return '<a href="%s?table_name=task&table_id=%d">%s</a>' % (url('/admin/yabiengine/syslog/'), self.id, "Syslog")
    link_to_syslog.allow_tags = True
    link_to_syslog.short_description = "Syslog"


class StageIn(models.Model, Editable):
    src = models.CharField(max_length=256)
    dst = models.CharField(max_length=256)
    order = models.IntegerField()
    task = models.ForeignKey(Task)
    method = models.CharField(max_length=5,choices=STAGING_COPY_CHOICES)

    @property
    def workflowid(self):
        return self.task.job.workflow.id


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
        return json.dumps({ 'table_name':self.table_name,
                            'table_id':self.table_id,
                            'message':self.message
                            }
                          )



