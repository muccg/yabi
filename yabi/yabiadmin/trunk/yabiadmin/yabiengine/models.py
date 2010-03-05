# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.conf import settings
from yabiadmin.yabmin.models import User
from yabiadmin.yabiengine import backendhelper
from yabiadmin.yabiengine.urihelper import uriparse
from django.utils import simplejson as json, webhelpers
from django.db.models.signals import post_save
from django.utils.webhelpers import url
import httplib, os
from yabiadmin.yabiengine.urihelper import uriparse, url_join
from urllib import urlencode

import logging
logger = logging.getLogger('yabiengine')


class Status(object):
    def get_status_colour(obj, status):
        if settings.STATUS['pending'] == status:
            return 'grey'
        elif settings.STATUS['ready'] == status:
            return 'orange'
        elif settings.STATUS['requested'] == status:
            return 'green'
        elif settings.STATUS['complete'] == status:
            return 'green'
        elif settings.STATUS['error'] == status:
            return 'red'

class Editable(object):
    @models.permalink
    def edit_url(obj):
        admin_str = 'admin:%s_%s_change' % (obj._meta.app_label, obj._meta.object_name.lower())
        return (admin_str, (obj.id,))

    def edit_link(obj):
        return '<a href="%s">Edit</a>' % obj.edit_url()
    edit_link.short_description = 'Edit'
    edit_link.allow_tags = True


class Workflow(models.Model, Editable, Status):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    json = models.TextField(blank=True)
    log_file_path = models.CharField(max_length=1000,null=True)
    last_modified_on = models.DateTimeField(null=True, auto_now=True, editable=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    status = models.TextField(max_length=64, blank=True)
    yabistore_id = models.IntegerField(null=True)                           # ALTER TABLE yabiengine_workflow ADD COLUMN yabistore_id INTEGER;
    stageout = models.CharField(max_length=1000)

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


class Job(models.Model, Editable, Status):
    workflow = models.ForeignKey(Workflow)
    order = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    cpus = models.CharField(max_length=64, null=True, blank=True)
    walltime = models.CharField(max_length=64, null=True, blank=True)
    status = models.CharField(max_length=64, blank=True)
    exec_backend = models.CharField(max_length=256)
    fs_backend = models.CharField(max_length=256)
    command = models.TextField()
    commandparams = models.TextField(blank=True)
    input_filetype_extensions = models.TextField(blank=True)
    stageout = models.CharField(max_length=1000, null=True)


    def __unicode__(self):
        return "%s - %s" % (self.workflow.name, self.order)

    def status_ready(self):
        return self.status == settings.STATUS['ready']

    def status_complete(self):
        return self.status == settings.STATUS['complete']

    @property
    def workflowid(self):
        return self.workflow.id


    def update_json(self, data={}):
        json_object = json.loads(self.workflow.json)
        job_id = int(self.order)
        assert json_object['jobs'][job_id]['jobId'] == job_id + 1 # jobs are 1 indexed in json

        # status
        json_object['jobs'][job_id]['status'] = self.status

        # data
        for key in data:
            json_object['jobs'][job_id][key] = data[key]

        #stageout
        if self.stageout:
            json_object['jobs'][job_id]['stageout'] = self.stageout

        self.workflow.json = json.dumps(json_object)
        self.workflow.save() # this triggers an update on yabistore


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
    working_dir = models.CharField(max_length=256, null=True, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)                  # if we are null, we behave the old way and use our task.id

    def json(self):
        # formulate our status url and our error url
        if 'YABIADMIN' in os.environ:                                                   # if we are forced to talk to a particular admin
            statusurl = "http://%sengine/status/task/%d"%(os.environ['YABIADMIN'],self.id)
            errorurl = "http://%sengine/error/task/%d"%(os.environ['YABIADMIN'],self.id)
        else:
            # use the yabiadmin embedded in this server
            statusurl = webhelpers.url("/engine/status/task/%d" % self.id)
            errorurl = webhelpers.url("/engine/error/task/%d" % self.id)

        fsscheme, fsbackend_parts = uriparse(self.job.fs_backend)

        output = {
            "yabiusername":self.job.workflow.user.name,
            "taskid":self.id,
            "statusurl":statusurl,
            "errorurl":errorurl,
            "stagein":[],
            "exec":{
                    "command":self.command,
                    "backend": url_join(self.job.exec_backend),
                    "fsbackend": url_join(self.job.fs_backend, self.working_dir),
                    "workingdir": os.path.join(fsbackend_parts.path,self.working_dir)
                    },
            "stageout":self.job.stageout+"/"+("" if not self.name else self.name+"/")
            }

        stageins = self.stagein_set.all()
        for s in stageins:
            src_backend = backendhelper.get_backendcredential_for_uri(self.job.workflow.user.name,s.src).backend
            src_scheme, src_rest = uriparse(s.src)
            dst_backend = backendhelper.get_backendcredential_for_uri(self.job.workflow.user.name,s.dst).backend
            dst_scheme, dst_rest = uriparse(s.dst)


            output["stagein"].append({"src":s.src, "dst":s.dst, "order":s.order})

        return json.dumps(output)

    def __unicode__(self):
        return self.job_identifier

    @property
    def workflowid(self):
        return self.job.workflow.id

    def link_to_syslog(self):
        return '<a href="%s?table_name=task&table_id=%d">%s</a>' % (url('/admin/yabiengine/syslog/'), self.id, "Syslog")
    link_to_syslog.allow_tags = True
    link_to_syslog.short_description = "Syslog"



class StageIn(models.Model, Editable):
    src = models.CharField(max_length=256)
    dst = models.CharField(max_length=256)
    order = models.IntegerField()
    task = models.ForeignKey(Task)

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

    except Exception, e:
        logger.critical(e)
        raise

    
def task_save(sender, **kwargs):
    logger.debug('')
    task = kwargs['instance']

    try:
        # get all the tasks for this job
        jobtasks = Task.objects.filter(job=task.job)
        running = False
        error = False
        score=0.0
        for task in jobtasks:
            status = task.status
            score += { 
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


# must import this here to avoid circular reference
from yabiengine import wfwrangler

