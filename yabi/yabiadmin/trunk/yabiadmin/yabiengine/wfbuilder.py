import logging
logger = logging.getLogger('yabiengine')
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog, StageIn
from yabiadmin.yabmin.models import Backend, BackendCredential, Tool, User
from yabiadmin.yabiengine.YabiJobException import YabiJobException
from yabiadmin.yabiengine.urihelper import uri_get_path, uri_get_scheme
from yabiadmin.yabiengine import backendhelper
import simplejson as json
import datetime

def build(username, wfjson):
    logger.debug('build')
    
    wfobj = json.loads(wfjson)


    try:
        user = User.objects.get(name=username)
        w = Workflow(name=wfobj["name"], json=wfjson, user=user)
        w.save()
    
        for i,job in enumerate(wfobj["jobs"]):
            logger.debug('in loop %s' % i)
            tool = Tool.objects.get(name=job["toolName"])

            if tool.backend.name == 'nullbackend':
                continue
            else:
                addJob(w, job, i)

    except ObjectDoesNotExist, e:
        logger.critical(e.message)
        raise



def addJob(workflow, jobobj, order):
    logger.debug('addJob')
    j = Job(workflow=workflow, order=order, start_time=datetime.datetime.now())
    j.save()


    # now work through the parameters in the jobobj to build up the command and commandparams fields
    # might need to pass in the tool and validate against it
