# -*- coding: utf-8 -*-
from os.path import splitext
import os
import uuid
from math import log10
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog, StageIn
from yabiadmin.yabmin.models import Backend, BackendCredential
from yabiadmin.yabiengine.YabiJobException import YabiJobException
from yabiadmin.yabiengine.urihelper import uriparse, url_join
from yabiadmin.yabiengine import backendhelper

import logging
logger = logging.getLogger('yabiengine')

from conf import config


def walk(workflow):
    logger.debug('')

    jobset = [X for X in workflow.job_set.all().order_by("order")]
    for job in jobset:
        logger.info('Walking job id: %s' % job.id)
        try:

            #check job status
            if not job.status_complete() and not job.status_ready():
                check_dependencies(job)
                prepare_tasks(job)
                prepare_job(job)
            else:
                logger.info('Job id: %s is %s' % (job.id, job.status))
                # check all the jobs are complete, if so, changes status on workflow
                incomplete_jobs = Job.objects.filter(workflow=job.workflow).exclude(status=settings.STATUS['complete'])
                if not len(incomplete_jobs):
                    job.workflow.status = settings.STATUS['complete']
                    job.workflow.save()
            
        except YabiJobException,e:
            logger.info("Caught YabiJobException with message: %s" % e)
            continue
        except ObjectDoesNotExist,e:
            logger.critical("ObjectDoesNotExist at wfwrangler.walk: %s" % e)
            import traceback
            logger.debug(traceback.format_exc())
            raise
        except Exception,e:
            logger.critical("Error in workflow wrangler: %s" % e)
            raise


def check_dependencies(job):
    """Check each of the dependencies in the jobs command params.
    Start with a ready value of True and if any of the dependecies are not ready set ready to False.
    """
    logger.debug('')
    logger.info('Check dependencies for jobid: %s...' % job.id)

    for param in eval(job.commandparams):

        if param.startswith("yabi://"):
            logger.info('Evaluating param: %s' % param)
            scheme, uriparts = uriparse(param)
            workflowid, jobid = uriparts.path.strip('/').split('/')
            param_job = Job.objects.get(workflow__id=workflowid, id=jobid)
            if param_job.status != settings.STATUS["complete"]:
                raise YabiJobException("Job command parameter not complete. Job:%s Param:%s" % (job.id, param))


def prepare_tasks(job):
    logger.debug('')
    logger.debug('=================================================== prepare_tasks ===========================================================')
    logger.info('Preparing tasks for jobid: %s...' % job.id)

    tasks_to_create = []

    # get the backend for this job
    exec_bc = backendhelper.get_backendcredential_for_uri(job.workflow.user.name,job.exec_backend)
    exec_be = exec_bc.backend
    fs_bc = backendhelper.get_backendcredential_for_uri(job.workflow.user.name,job.fs_backend)
    fs_be = fs_bc.backend
    logger.debug("wfwrangler::prepare_tasks() exec_be:%s exec_bc:%s fs_be:%s fs_bc:%s"%(exec_be,exec_bc,fs_be,fs_bc))

    # reconstitute the input filetype extension list so each create_task can use it
    if job.input_filetype_extensions:
        job.extensions = eval(job.input_filetype_extensions)
    else:
        job.extensions = []

    paramlist = eval(job.commandparams)

    if paramlist:
        # this creates batch_on_param tasks
        logger.debug("PROCESSING batch on param")
        for param in paramlist:
            logger.debug("Prepare_task PARAMLIST: %s"%paramlist)

            # TODO: fix all this voodoo

            ##################################################
            # handle yabi:// uris
            # fetches the stageout of previous job and
            # adds that to paramlist to be processed
            ##################################################
            if param.startswith("yabi://"):
                logger.info('Processing uri %s' % param)

                # parse yabi uri
                # we may want to look up workflows and jobs on specific servers later,
                # but just getting path for now as we have just one server
                scheme, uriparts = uriparse(param)
                workflowid, jobid = uriparts.path.strip('/').split('/')
                param_job = Job.objects.get(workflow__id=workflowid, id=jobid)

                # get stage out directory of job
                stageout = param_job.stageout

                paramlist.append(stageout)


            ##################################################
            # handle yabifs:// uris that are directories
            ##################################################

            # uris ending with a / on the end of the path are directories
            elif param.startswith("yabifs://") and param.endswith("/"):
                logger.info('Processing uri %s' % param)

                logger.debug("PROCESSING")
                logger.debug("%s -> %s" % (param, backendhelper.get_file_list(job.workflow.user.name, param)))

                # get_file_list will return a list of file tuples
                for f in backendhelper.get_file_list(job.workflow.user.name, param):
                    logger.debug("FILELIST %s" % f)
                    tasks_to_create.append([job, param, f[0], exec_be, exec_bc, fs_be, fs_bc])


            ##################################################
            # handle yabifs:// uris
            ##################################################
            elif param.startswith("yabifs://"):
                logger.info('Processing uri %s' % param)            
                rest, filename = param.rsplit("/",1)
                tasks_to_create.append([job, rest + "/", filename, exec_be, exec_bc, fs_be, fs_bc])


            ##################################################
            # handle gridftp:// gridftp uris that are directories
            ##################################################

            # uris ending with a / on the end of the path are directories
            elif param.startswith("gridftp://") and param.endswith("/"):
                logger.info('Processing uri %s' % param)

                logger.debug("PROCESSING")
                logger.debug("%s -> %s" % (param, backendhelper.get_file_list(job.workflow.user.name, param)))

                # get_file_list will return a list of file tuples
                for f in backendhelper.get_file_list(job.workflow.user.name, param):
                    tasks_to_create.append([job, param, f[0], exec_be, exec_bc, fs_be, fs_bc])


            ##################################################
            # handle gridftp:// uris
            ##################################################
            elif param.startswith("gridftp://"):
                logger.info('Processing uri %s' % param)            
                rest, filename = param.rsplit("/",1)

                logger.debug("PROCESSING %s" % param)

                tasks_to_create.append([job, rest + "/", filename, exec_be, exec_bc, fs_be, fs_bc])


            ##################################################
            # handle unknown types
            ##################################################
            else:
                logger.info('****************************************')
                logger.info('Unhandled type: ' + param)
                logger.info('****************************************')
                raise Exception('Unknown file type.')
            

    else:
        # This creates NON batch on param jobs
        logger.debug("PROCESSING NON batch on param")
        tasks_to_create.append([job, None, None, exec_be, exec_bc, fs_be, fs_bc])
        

    ##
    ## now loop over these tasks and actually create them
    ##
    
    num = 1
    
    # lets count up our paramlist to see how many 'real' (as in not yabi://) files there are to process
    # won't count tasks with file == None as these are from not batch param jobs
    count = len([X for X in tasks_to_create if X[2] and is_task_file_valid(X[0],X[2])])
        
     # lets build a closure that will generate our names for us
    if count>1:
        # the 10 base logarithm will give us how many digits we need to pad
        buildname = lambda n: (n+1,("0"*(int(log10(count))+1)+str(n))[-(int(log10(count))+1):])
    else:
        buildname = lambda n: (n+1, "")
    
    logger.debug("TASKS TO CREATE: %s" % tasks_to_create)
    
    # build the first name
    num, name = buildname(num)
    for task_data in tasks_to_create:
        job, file = task_data[0], task_data[2]
        # we should only create a task file if job file is none ie it is a non batch_on_param task
        # or if it is a valid filetype for the batch_on_param
        # TODO REFACTOR - Adam can you look at how this is done
        if file == None or is_task_file_valid(job, file):
            if create_task( *(task_data+[name]) ):
                # task created, bump task
                num,name = buildname(num)


def prepare_job(job):
    logger.debug('')
    logger.info('Setting job id %s to ready' % job.id)                
    job.status = settings.STATUS["ready"]
    job.save()


def is_task_file_valid(job,file):
    """returns a boolean shwoing if the file passed in is a valid file for the job. Only uses the file extension to tell"""
    return splitext(file)[1].strip('.') in job.extensions


def create_task(job, param, file, exec_be, exec_bc, fs_be, fs_bc, name=""):
    logger.debug('START TASK CREATION')
    logger.debug("job %s" % job)
    logger.debug("file %s" % file)
    logger.debug("param %s" % param)
    logger.debug("exec_be %s" % exec_be)
    logger.debug("exec_bc %s" % exec_bc)
    logger.debug("fs_be %s" % fs_be)
    logger.debug("fs_bc %s" % fs_bc)

    # TODO param is uri less filename gridftp://amacgregor@xe-ng2.ivec.org/scratch/bi01/amacgregor/
    # rename it to something sensible

    # create the task
    t = Task(job=job, status=settings.STATUS['pending'])
    t.working_dir = str(uuid.uuid4()) # random uuid
    t.name = name
    t.command = job.command
    t.expected_ip = config.config['backend']['port'][0]
    t.expected_port = config.config['backend']['port'][1]
    t.save()

    # basic stuff used by both stagein types
    fsscheme, fsbackend_parts = uriparse(job.fs_backend)
    execscheme, execbackend_parts = uriparse(job.exec_backend)


    ##
    ## JOB STAGEINS
    ##
    ## This section catches all non-batch param files which should appear in job_stageins on job in db
    ##
    ## Take each job stagein
    ## Add a stagein in the database for it
    ## Replace the filename in the command with relative path used in the stagein
    for job_stagein in set(eval(job.job_stageins)): # use set to get unique files
        logger.debug("CREATING JOB STAGEINS")

        if "/" not in job_stagein:
            continue

        dirpath, filename = job_stagein.rsplit("/",1)
        scheme, rest = uriparse(dirpath)

        if scheme not in settings.VALID_SCHEMES:
            continue

        t.command = t.command.replace(job_stagein, url_join(fsbackend_parts.path,t.working_dir, "input", filename))

        create_stagein(task=t, param=dirpath+'/', file=filename, scheme=fsscheme,
                       hostname=fsbackend_parts.hostname,
                       path=os.path.join(fsbackend_parts.path, t.working_dir, "input", filename),
                       username=fsbackend_parts.username)

        logger.debug('JOB STAGEIN')
        logger.debug("dirpath %s" % dirpath )
        logger.debug("filename %s" % filename)


    ##
    ## BATCH PARAM STAGEINS
    ##
    ## This section catches all batch-param files
        
    # only make tasks for expected filetypes
    if file and is_task_file_valid(job,file):
        logger.debug("CREATING BATCH PARAM STAGEINS for %s" % file)
        
        param_scheme, param_uriparts = uriparse(param)
        root, ext = splitext(file)

        # add the task specific file replacing the % in the command line
        t.command = t.command.replace("%", url_join(fsbackend_parts.path,t.working_dir, "input", file))

        create_stagein(task=t, param=param, file=file, scheme=fsscheme,
                       hostname=fsbackend_parts.hostname,
                       path=os.path.join(fsbackend_parts.path, t.working_dir, "input", file),
                       username=fsbackend_parts.username)


    
    t.status = settings.STATUS['ready']
    t.save()

    logger.debug('saved========================================')
    logger.info('Creating task for job id: %s using command: %s' % (job.id, t.command))
    logger.info('working dir is: %s' % (t.working_dir) )

                
    # return true indicates that we actually made a task
    return True 


def create_stagein(task=None, param=None, file=None, scheme=None, hostname=None, path=None, username=None):
    s = StageIn(task=task,
                src="%s%s" % (param, file),
                dst="%s://%s@%s%s" % (scheme, username, hostname, path),
                order=0)

    logger.debug("Stagein: %s <=> %s " % (s.src, s.dst))
    s.save()
        
