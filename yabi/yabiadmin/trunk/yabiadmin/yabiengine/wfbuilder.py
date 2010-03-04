# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.conf import settings
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog, StageIn
from yabiadmin.yabmin.models import Backend, BackendCredential, Tool, User
from yabiadmin.yabiengine.YabiJobException import YabiJobException
from yabiadmin.yabiengine import backendhelper
from django.utils import simplejson as json
from yabiengine import wfwrangler
import datetime
import os

import logging
logger = logging.getLogger('yabiengine')


job_cache = {}

def build(username, workflow_json):
    logger.debug('')
    
    workflow_dict = json.loads(workflow_json)
    job_cache = {}

    try:

        user = User.objects.get(name=username)
        workflow = Workflow(name=workflow_dict["name"], json=workflow_json, user=user)
        workflow.save()

        # sort out the stageout directory
        if 'default_stageout' in workflow_dict and workflow_dict['default_stageout']:
            default_stageout = workflow_dict['default_stageout']
        else:
            default_stageout = user.default_stageout
            
        workflow.stageout = "%s%s/" % (default_stageout, workflow.name)
        workflow.status = settings.STATUS['ready']
        workflow.save()
        backendhelper.mkdir(workflow.user.name, workflow.stageout)

        for i,job_dict in enumerate(workflow_dict["jobs"]):
            job = addJob(workflow, job_dict, i)

        # start processing
        logger.debug('-----Starting workflow id %d -----' % workflow.id)
        wfwrangler.walk(workflow)

        return workflow.yabistore_id
    

    except ObjectDoesNotExist, e:
        logger.critical(e)
        raise
    except KeyError, e:
        logger.critical(e)
        raise
    except Exception, e:
        logger.critical(e)
        import traceback
        logger.debug(traceback.format_exc())
        raise



def addJob(workflow, job_dict, order):
    logger.debug('')

    tool = Tool.objects.get(name=job_dict["toolName"])

    job = Job(workflow=workflow, order=order, start_time=datetime.datetime.now())
    job.save()

    # cache job for later reference
    job_id = job_dict["jobId"] # the id that is used in the json
    job_cache[job_id] = job

    # process the parameterList to get a useful dict
    logger.debug("Process parameterList")
    param_dict = {}
    for toolparam in job_dict["parameterList"]["parameter"]:
        logger.debug('TOOLPARAM:%s'%(toolparam))
        param_dict[toolparam["switchName"]] = get_param_value(workflow, toolparam, job)
        
    logger.debug("param_dict = %s"%(param_dict))

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
            commandparams.extend(param_dict[tp.switch])
            param_dict[tp.switch] = '%' # use place holder now in command

        # run through all the possible switch uses
        switchuse = tp.switch_use.value

        if switchuse == 'switchOnly':
            command.append(tp.switch)

        elif switchuse == 'valueOnly':
            command.append(param_dict[tp.switch][0])

        elif switchuse == 'both':
            command.append("%s %s" % (tp.switch, param_dict[tp.switch][0]))

        elif switchuse == 'combined':
            command.append("%s%s" % (tp.switch, param_dict[tp.switch][0]))

        elif switchuse == 'pair':
            pass # TODO figure out what to do with this one

        elif switchuse == 'none':
            pass


    # add other attributes
    job.command = ' '.join(command)
    logger.debug("JOB PRE PARAMS: %s"%job.commandparams)
    job.commandparams = repr(commandparams) # save string repr of list
    logger.debug("JOB POST PARAMS: %s"%job.commandparams)
    
    # set status to complete if null backend
    if tool.backend.name == 'nullbackend':
        job.status = settings.STATUS['complete']
    else:
        job.status = settings.STATUS['pending']

    # add a list of input file extensions as string, we will reconstitute this for use in the wfwrangler
    job.input_filetype_extensions = str(tool.input_filetype_extensions())

    try:
        ebcs = BackendCredential.objects.filter(credential__user=workflow.user, backend=tool.backend)
        
        logger.debug("EBCS returned: %s"%(ebcs))
        
        for bc in ebcs:
            logger.debug("%s: Backend: %s Credential: %s"%(bc,bc.credential,bc.backend))
        
        #exec_backendcredential = backendhelper.get_backendcredential_for_uri(yabiusername, uri)
        
        exec_backendcredential = BackendCredential.objects.get(credential__user=workflow.user, backend=tool.backend)
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        logger.critical('Invalid credentials for user: %s and backend: %s' % (workflow.user, tool.backend))
        raise
    try:
        # TODO: select the correct fsbackend here...
        logger.debug("fetching fsbackends...")
        
        ebcs = BackendCredential.objects.filter(credential__user=workflow.user, backend=tool.fs_backend)
        for bc in ebcs:
            logger.debug("%s: Backend: %s Credential: %s"%(bc,bc.credential,bc.backend))
        
        fs_backendcredential = BackendCredential.objects.get(credential__user=workflow.user, backend=tool.fs_backend)
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        logger.critical('Invalid credentials for user: %s and backend: %s' % (workflow.user, tool.fs_backend))
        raise


    #TODO hardcoded
    if tool.backend.name == 'nullbackend':
        job.stageout = None
    else:
        job.stageout = "%s%s/" % (workflow.stageout, "%d - %s"%(job.order+1,tool.display_name) )
        
        # make that directory
        backendhelper.mkdir(workflow.user.name, job.stageout)

    job.exec_backend = exec_backendcredential.homedir_uri
    job.fs_backend = fs_backendcredential.homedir_uri

    job.cpus = tool.cpus
    job.walltime = tool.walltime
    job.save()


def get_param_value(workflow, tp, job):
    logger.debug('')

    logger.debug("======= get_param_value =============: %s" % tp)
    
    value = []
    if type(tp["value"]) == list:
        # parameter input is multiple input files. loop ofer these files
        for item in tp["value"]:

            if type(item) == dict:

                # handle links to previous nodes
                if 'type' in item and 'jobId' in item:
                    # TODO - adding localhost.localdomain to uri at the moment, should this be pulled in from somewhere

                    previous_job = job_cache[item['jobId']]

                    if previous_job.stageout == None:
                        value = eval(previous_job.commandparams)
                    else:
                        value = [u"yabi://localhost.localdomain/%d/%d/" % (workflow.id, job_cache[item['jobId']].id)]

                # handle links to previous file selects
                elif 'type' in item and 'filename' in item and 'root' in item:
                    if item['type'] == 'file':
                        path = ''
                        if item['path']:
                            path = os.path.join(*item['path'])
                            if not path.endswith(os.sep):
                                path = path + os.sep
                        value.append( '%s%s%s' % (item['root'], path, item['filename']) )
                    elif item['type'] == 'directory':
                        fulluri = item['root']+item['filename']+'/'
                            
                        # get recursive directory listing
                        filelist = backendhelper.get_file_list(job.workflow.user.name, fulluri, recurse=True)
                            
                        logger.debug("FILELIST returned:%s"%str(filelist))
                        
                        value.extend( [ fulluri + X[0] for X in filelist ] )
                
            elif type(item) == str or type(item) == unicode:
                value.append( item )

    logger.debug("get_param_value() returning: %s"%value)
    return value


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    TODO this function is from djangos defaultfilters.py which is not in mango
    we should work on getting these back into mango and take advantage of all
    of djangos safe string stuff
    """
    logger.debug('')

    import unicodedata
    import re
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)
