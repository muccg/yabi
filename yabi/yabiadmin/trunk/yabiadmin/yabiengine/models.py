from django.db import models
from django.conf import settings
from yabiadmin.yabmin.models import User
from yabiadmin.yabiengine import backendhelper
from django.utils import simplejson as json, webhelpers


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
    
    def __unicode__(self):
        return self.name

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

    def __unicode__(self):
        return "%s - %s" % (self.workflow.name, self.order)

    def status_ready(self):
        return self.status == settings.STATUS['ready']

    def status_complete(self):
        return self.status == settings.STATUS['complete']
    



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
    
    def json(self):

        output = {
            "yabiusername":self.job.workflow.user.name,
            "taskid":self.id,
            "statusurl":webhelpers.url("/engine/status/task/%d" % self.id),
            "errorurl":webhelpers.url("/engine/error/task/%d" % self.id),
            "stagein":[],
            "exec":{
            "command":self.command,
            "backend":backendhelper.get_backend_from_uri(self.job.exec_backend).name,
            "fsbackend":backendhelper.get_backend_from_uri(self.job.fs_backend).name,
            },
            "stageout":self.job.stageout
            }

        stageins = self.stagein_set.all()
        for s in stageins:
            output["stagein"].append({"srcbackend":s.src, "srcpath":s.src, "dstbackend":s.dst, "dstpath":s.dst, "order":s.order})

        return json.dumps(output)

    def __unicode__(self):
        return self.job_identifier



class StageIn(models.Model):
    src = models.CharField(max_length=256)
    dst = models.CharField(max_length=256)
    order = models.IntegerField()
    task = models.ForeignKey(Task)

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
