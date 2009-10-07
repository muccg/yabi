from django.db import models
from django.db.models import Q
from django.conf import settings
from yabiadmin.yabmin.models import User
from yabiadmin.yabiengine import backendhelper
from yabiadmin.yabiengine.urihelper import uriparse, uri_get_pseudopath
from django.utils import simplejson as json, webhelpers
from django.db.models.signals import post_save
from django.utils.webhelpers import url
import httplib, os
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
        # formulate our status url and our error url
        if 'YABIADMIN' in os.environ:                                                   # if we are forced to talk to a particular admin
            statusurl = "http://%sengine/status/task/%d"%(os.environ['YABIADMIN'],self.id)
            errorurl = "http://%sengine/error/task/%d"%(os.environ['YABIADMIN'],self.id)
        else:
            # use the yabiadmin embedded in this server
            statusurl = webhelpers.url("/engine/status/task/%d" % self.id)
            errorurl = webhelpers.url("/engine/error/task/%d" % self.id)
            

        output = {
            "yabiusername":self.job.workflow.user.name,
            "taskid":self.id,
            "statusurl":statusurl,
            "errorurl":errorurl,
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
    print "POST",resource,data
    r = conn.getresponse()
    
    status = r.status
    data = r.read()
    
    logger.debug(status)
    logger.debug(data)
    
    return status,data


def workflow_save(sender, **kwargs):
    logger.debug('')
    workflow = kwargs['instance']
    
    print "WORKFLOW SAVE",workflow

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
        print "workflow_save::yabistoreupdate",resource,data
        status, data = yabistore_update(resource, data)

        print "status",repr(status)
        print "data",repr(data)
        
        # if this was created. save the returned id into yabistore_id
        if kwargs['created']:
            print "SAVING WFID"
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
        # update the yabistore
        if kwargs['created']:
            resource = os.path.join(settings.YABISTORE_BASE,"jobs",job.workflow.user.name)
        else:
            resource = os.path.join(settings.YABISTORE_BASE,"jobs",job.workflow.user.name, job.id)

        data = {'status':t.status }
        print "job_save::yabistore_update(",resource,",", data,")"

    except Exception, e:
        logger.critical(e)
        raise

    

def task_save(sender, **kwargs):
    logger.debug('')
    task = kwargs['instance']

    try:
        # update the yabistore
        if kwargs['created']:
            resource = os.path.join(settings.YABISTORE_BASE,'tasks',task.job.workflow.user.name)
        else:
            resource = os.path.join(settings.YABISTORE_BASE,'tasks',task.job.workflow.user.name, str(task.id) )

        data = {'error_msg':task.error_msg,
                'status':task.status
                }
        
        print "task_save::OLD_UPDATE",resource,data
        #yabistore_update(resource, data)

        #from django.db.models import Count
        total = len(Task.objects.filter(job=task.job))
        done = len(Task.objects.filter(job=task.job,status=settings.STATUS['complete']))

        print "%d/%d"%(done,total)
        
        print "job:",task.job
        print "job id:",task.job.order
        
        # work out if this job is in an error state
        errored = [X for X in Task.objects.filter(job=task.job,status=settings.STATUS['error'])]
        erroredcount = len(errored)
        
        # how tasks are still ready. If they are all still ready, then the task is not runnig
        running = len(Task.objects.filter(job=task.job).filter(Q(status=settings.STATUS['ready'])|Q(status=settings.STATUS['requested'])))<total
        
        status = "completed" if done==total else "error" if errored else "running" if running else "pending"
        
        errorMessage = None if not erroredcount else errored[0].error_msg
        
        if len(errored):
            print "message=",errored[0].error_msg
        
        if not kwargs['created']:
            resource = os.path.join(settings.YABISTORE_BASE,'workflows',task.job.workflow.user.name, str(task.job.workflow.yabistore_id), str(task.job.order) )
            data = dict(    status=status,
                            tasksComplete=float(done),
                            tasksTotal=float(total)
                        )
            if errorMessage:
                data['errorMessage']=errorMessage
                            
            print "task_save::yabistoreupdate",resource,data
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

