from django.db import models
from yabiadmin.yabmin.models import User
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
    cpus = models.IntegerField(null=True)
    walltime = models.IntegerField(null=True)
    stageout = models.CharField(max_length=1000, null=True)
    status = models.CharField(max_length=64, blank=True)
    command = models.TextField()
    commandparams = models.TextField(blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.workflow.name, self.order)


class Task(models.Model):
    job = models.ForeignKey(Job)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    job_identifier = models.TextField()
    command = models.TextField(blank=True)
    exec_backend = models.CharField(max_length=256)
    fs_backend = models.CharField(max_length=256)
    error_msg = models.CharField(max_length=1000, null=True)
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
            "backend":self.exec_backend,
            "fsbackend":self.fs_backend,
            },
            "stageout":self.job.stageout
            }

        stageins = self.stagein_set.all()
        for s in stageins:
            output["stagein"].append({"srcbackend":s.src_backend, "srcpath":s.src_path, "dstbackend":s.dst_backend, "dstpath":s.dst_path.strip(), "order":s.order})

        return json.dumps(output)


class StageIn(models.Model):
    src_backend = models.CharField(max_length=256)
    src_path = models.TextField()
    dst_backend = models.CharField(max_length=256)
    dst_path = models.TextField()
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

    def __unicode__(self):
        return self.message

    def json(self):
        return json.dumps({ 'table_name':self.table_name,
                            'table_id':self.table_id,
                            'message':self.message
                            }
                          )
