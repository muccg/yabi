from django.db import models
from django.conf import settings
from yabiadmin.yabmin.models import User
from yabiadmin.yabiengine import backendhelper
from yabiadmin.yabiengine.urihelper import uriparse, uri_get_pseudopath
from django.utils import simplejson as json, webhelpers
from django.db.models.signals import post_save
from django.utils.webhelpers import url
import httplib
from urllib import urlencode

import logging
import yabilogging
logger = logging.getLogger('yabiengine')


class Workflow(models.Model):
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

    def __unicode__(self):
        return self.name

    @property
    def workflowid(self):
        return self.id
    
class Job(models.Model):
    workflow = models.ForeignKey(Workflow)
    order = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    cpus = models.CharField(max_length=64, null=True, blank=True)
    walltime = models.CharField(max_length=64, null=True, blank=True)
    stageout = models.CharField(max_length=1000, null=True)
    status = models.CharField(max_length=64, blank=True)
    exec_backend = models.CharField(max_length=256)
    fs_backend = models.CharField(max_length=256)
    command = models.TextField()
    commandparams = models.TextField(blank=True)
    input_filetype_extensions = models.TextField(blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.workflow.name, self.order)

    def status_ready(self):
        return self.status == settings.STATUS['ready']

    def status_complete(self):
        return self.status == settings.STATUS['complete']

    @property
    def workflowid(self):
        return self.workflow.id

class Task(models.Model):
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

    
    def json(self):

        output = {
            "yabiusername":self.job.workflow.user.name,
            "taskid":self.id,
            "statusurl":webhelpers.url("/engine/status/task/%d" % self.id),
            "errorurl":webhelpers.url("/engine/error/task/%d" % self.id),
            "stagein":[],
            "exec":{
            "command":self.command,
            "backend": "%s%s" % (self.job.exec_backend, self.working_dir),
            "fsbackend": "%s%s" % (self.job.fs_backend, self.working_dir),
            },
            "stageout":self.job.stageout
            }

        stageins = self.stagein_set.all()
        for s in stageins:
            src_backend = backendhelper.get_backend_from_uri(s.src).name
            src_scheme, src_rest = uriparse(s.src)
            dst_backend = backendhelper.get_backend_from_uri(s.dst).name
            dst_scheme, dst_rest = uriparse(s.dst)


            output["stagein"].append({"src":s.src, "dst":s.dst, "order":s.order})

        return json.dumps(output)

    def __unicode__(self):
        return self.job_identifier

    @property
    def workflowid(self):
        return self.job.workflow.id



class StageIn(models.Model):
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


# TODO make this more robust.
# add exceptions
def yabistore_update(resource, data):
    logger.debug('')
    data = urlencode(data)
    headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
    conn = httplib.HTTPConnection(settings.YABISTORE_SERVER)
    conn.request('POST', resource, data, headers)
    r = conn.getresponse()
    
    status = r.status
    data = r.read()
    
    logger.debug(status)
    logger.debug(data)
    
    return status,data


def workflow_save(sender, **kwargs):
    logger.debug('')
    workflow = kwargs['instance']

    try:
        # update the yabistore
        if kwargs['created']:
            resource = '%s/workflows/%s/' % (settings.YABISTORE_BASE, workflow.user.name)
        else:
            resource = '%s/workflows/%s/%d' % (settings.YABISTORE_BASE, workflow.user.name, workflow.yabistore_id)

        data = {'json':workflow.json,
                'name':workflow.name,
                'status':workflow.status
                }
        status, data = yabistore_update(resource, data)

        print "status",repr(status)
        print "data",repr(data)
        
    except Exception, e:
        logger.critical(e)
        raise


def job_save(sender, **kwargs):
    logger.debug('')
    job = kwargs['instance']

    try:
        # update the yabistore
        if kwargs['created']:
            resource = '%s/jobs/%s/' % (settings.YABISTORE_BASE, job.workflow.user.name)
        else:
            resource = '%s/jobs/%s/%s' % (settings.YABISTORE_BASE, job.workflow.user.name, job.id)

        data = {'status':t.status }
        yabistore_update(resource, data)

    except Exception, e:
        logger.critical(e)
        raise

    

def task_save(sender, **kwargs):
    logger.debug('')
    task = kwargs['instance']

    try:
        # update the yabistore
        if kwargs['created']:
            resource = '%s/tasks/%s/' % (settings.YABISTORE_BASE,task.job.workflow.user.name)
        else:
            resource = '%s/tasks/%s/%s' % (settings.YABISTORE_BASE, task.job.workflow.user.name, task.id)

        data = {'error_msg':task.error_msg,
                'status':task.status
                }
        yabistore_update(resource, data)

        #Checks all the tasks are complete, if so, changes status on job
        #and triggers the workflow walk
        incomplete_tasks = Task.objects.filter(job=task.job).exclude(status=settings.STATUS['complete'])
        if not incomplete_tasks:
            task.job.status = settings.STATUS['complete']
            task.job.save()
            wfwrangler.walk(task.job.workflow)

        # check for error status
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


# must import this here to avoid circular reference
from yabiengine import wfwrangler

