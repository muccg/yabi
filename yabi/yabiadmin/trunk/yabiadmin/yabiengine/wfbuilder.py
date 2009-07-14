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

job_cache = {}

def build(username, workflow_json):
    logger.debug('build')
    
    workflow_dict = json.loads(workflow_json)
    job_cache = {}

    try:
        user = User.objects.get(name=username)
        workflow = Workflow(name=workflow_dict["name"], json=workflow_json, user=user)
        workflow.save()
    
        for i,job_dict in enumerate(workflow_dict["jobs"]):
            job = addJob(workflow, job_dict, i)

    except ObjectDoesNotExist, e:
        logger.critical(e.message)
        raise
    except KeyError, e:
        logger.critical(e.message)
        raise




def addJob(workflow, job_dict, order):
    logger.debug('addJob')

    tool = Tool.objects.get(name=job_dict["toolName"])

    # add a job, return None if no backend as nothing needs to be run
    if tool.backend.name == 'nullbackend':
        return None
    job = Job(workflow=workflow, order=order, start_time=datetime.datetime.now())
    job.save()




    # process the parameterList to get a useful dict
    param_dict = {}
    for tp in job_dict["parameterList"]["parameter"]:
            param_dict[tp["switchName"]] = get_param_value(workflow, tp)

    logger.info("Param_Dict: %s" % param_dict)

    # now build up the command
    command = []
    commandparams = []

    command.append(tool.path)

    for tp in tool.toolparameter_set.order_by('rank').all():

        # check the tool switch against the incoming params
        if tp.switch not in param_dict:
            continue

        # if the switch is the batch on param switch put it in commandparams and add placeholder in command
        if tp == tool.batch_on_param:
            commandparams.append(param_dict[tp.switch])
            param_dict[tp.switch] = '%' # use place holder now in command

        # run through all the possible switch uses
        switchuse = tp.switch_use.value

        if switchuse == 'switchOnly':
            command.append(tp.switch)

        elif switchuse == 'valueOnly':
            command.append(param_dict[tp.switch])

        elif switchuse == 'both':
            command.append("%s %s" % (tp.switch, param_dict[tp.switch]))

        elif switchuse == 'combined':
            command.append("%s%s" % (tp.switch, param_dict[tp.switch]))

        elif switchuse == 'pair':
            pass # TODO figure out what to do with this one

        elif switchuse == 'none':
                pass


    # now save the command and commandparams
    job.command = ' '.join(command)
    job.commandparams = repr(commandparams) # save string repr of list
    job.status = settings.STATUS['pending']
    job.save()

    # cache job for later reference
    job_id = job_dict["jobId"] # the id that is used in the json
    job_cache[job_id] = job




def get_param_value(workflow, tp):
    value = ''
    if type(tp["value"]) == list:
        for item in tp["value"]:

            if type(item) == dict:

                if 'type' in item and 'jobId' in item:
                    value = u"yabi://%d/%d/" % (workflow.id, job_cache[item['jobId']].id)
                
            elif type(item) == str or type(item) == unicode:
                value += item

    return value

