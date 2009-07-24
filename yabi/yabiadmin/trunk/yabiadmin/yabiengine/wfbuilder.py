import logging
logger = logging.getLogger('yabiengine')
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog, StageIn
from yabiadmin.yabmin.models import Backend, BackendCredential, Tool, User
from yabiadmin.yabiengine.YabiJobException import YabiJobException
from yabiadmin.yabiengine.urihelper import get_backend_uri, uri_get_pseudopath
from yabiadmin.yabiengine import backendhelper
from django.utils import simplejson as json
import datetime

job_cache = {}

def build(username, workflow_json):
    logger.debug('build')

    logger.debug(workflow_json)
    
    workflow_dict = json.loads(workflow_json)
    job_cache = {}

    try:
        user = User.objects.get(name=username)
        workflow = Workflow(name=slugify(workflow_dict["name"]), json=workflow_json, user=user)
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


    # add other attributes
    job.command = ' '.join(command)
    job.commandparams = repr(commandparams) # save string repr of list
    job.status = settings.STATUS['pending']


    ## TODO raise error when no credential for user
    backendcredential = BackendCredential.objects.get(credential__user=workflow.user, backend=tool.fs_backend)
    # HACK change the first occurance of username from backend username to yabi username
    # TODO fix this
    bc_homedir = backendcredential.homedir.replace(backendcredential.credential.username, backendcredential.credential.user.name, 1)
    stageout = "%s%d/%d/" % (bc_homedir, workflow.id, job.id)
    job.stageout = stageout
    job.exec_backend = get_backend_uri(tool.backend)
    job.fs_backend = get_backend_uri(tool.fs_backend)

    job.cpus = tool.cpus
    job.walltime = tool.walltime
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
                    # TODO - adding localhost.localdomain to uri at the moment, should this be pulled in from somewhere
                    value = u"yabi://localhost.localdomain/%d/%d/" % (workflow.id, job_cache[item['jobId']].id)
                
            elif type(item) == str or type(item) == unicode:
                value += item

    return value



def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    TODO this function is from djangos defaultfilters.py which is not in mango
    we should work on getting these back into mango and take advantage of all
    of djangos safe string stuff
    """
    import unicodedata
    import re
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)
