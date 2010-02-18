# -*- coding: utf-8 -*-
from os.path import splitext
import os
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog, StageIn
from yabiadmin.yabmin.models import Backend, BackendCredential
from yabiadmin.yabiengine.YabiJobException import YabiJobException
from yabiadmin.yabiengine.urihelper import uriparse
from yabiadmin.yabiengine import backendhelper

import logging
logger = logging.getLogger('yabiengine')

import urlparse
import re
re_url_schema = re.compile(r'\w+')

def parse_url(uri):
    """Parse a url via the inbuilt urlparse. But this is slightly different
    as it can handle non-standard schemas. returns the schema and then the
    tuple from urlparse"""
    scheme, rest = uri.split(":",1)
    assert re_url_schema.match(scheme)
    return scheme, urlparse.urlparse(rest)


# this is used to join subpaths to already cinstructed urls
def url_join(*args):
    return reduce(lambda a,b: a+b if a.endswith('/') else a+'/'+b, args)

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
    logger.info('Preparing tasks for jobid: %s...' % job.id)

    input_files = []

    # get the backend for this job
    #exec_be = backendhelper.get_backend_for_uri(job.workflow.user.name,job.exec_backend)
    #exec_bc = BackendCredential.objects.get(credential__user__name=job.workflow.user.name, backend=exec_be, credential__user=job.workflow.user)
    #fs_be = backendhelper.get_backend_for_uri(job.workflow.user.name,job.fs_backend)
    #fs_bc = BackendCredential.objects.get(credential__user__name=job.workflow.user.name, backend=fs_be, credential__user=job.workflow.user)
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

    if not paramlist:
        # job operates without batchonparam
        t = Task(job=job, command=job.command, status="ready")
        t.save()
        
    
    for num,param in enumerate(paramlist):

        #TODO refactor each of these code blocks into handlers
        logger.debug("PARAM: %s" % param)

        ##################################################
        # handle yabi:// uris
        ##################################################
        if param.startswith("yabi://"):
            logger.info('Processing uri %s' % param)

            # parse yabi uri
            # TODO we may want to look at server later, but just getting path for now
            scheme, uriparts = uriparse(param)
            workflowid, jobid = uriparts.path.strip('/').split('/')
            param_job = Job.objects.get(workflow__id=workflowid, id=jobid)
            
            # get stage out directory of job
            stageout = param_job.stageout

            paramlist.append(stageout)


        ##################################################
        # handle file:// uris that are directories
        ##################################################

        # uris ending with a / on the end of the path are directories
        elif param.startswith("yabifs://") and param.endswith("/"):
            logger.info('Processing uri %s' % param)
    
            logger.debug("PROCESSING")
            logger.debug("%s -> %s" % (param, backendhelper.get_file_list(job.workflow.user.name, param)))

            # get_file_list will return a list of file tuples
            for f in backendhelper.get_file_list(job.workflow.user.name, param):
                logger.debug("FILELIST %s" % f)
                create_task(job, param, f[0], exec_be, exec_bc, fs_be, fs_bc,name=("0000"+str(num))[-4:])


        ##################################################
        # handle file:// uris
        ##################################################
        elif param.startswith("yabifs://"):
            logger.info('Processing uri %s' % param)            
            rest, filename = param.rsplit("/",1)
            create_task(job, rest + "/", filename, exec_be, exec_bc, fs_be, fs_bc,name=("0000"+str(num))[-4:])
            input_files.append(param)


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
                create_task(job, param, f[0], exec_be, exec_bc, fs_be, fs_bc,name=("0000"+str(num))[-4:])


        ##################################################
        # handle file:// uris
        ##################################################
        elif param.startswith("gridftp://"):
            logger.info('Processing uri %s' % param)            
            rest, filename = param.rsplit("/",1)
            
            logger.debug("PROCESSING %s" % param)
            
            create_task(job, rest + "/", filename, exec_be, exec_bc, fs_be, fs_bc,name=("0000"+str(num))[-4:])
            input_files.append(param)
            
            

        ##################################################
        # handle unknown types
        ##################################################
        else:
            logger.info('****************************************')
            logger.info('Unhandled type: ' + param)
            logger.info('****************************************')


def prepare_job(job):
    logger.debug('')
    logger.info('Setting job id %s to ready' % job.id)                
    job.status = settings.STATUS["ready"]
    job.save()





def create_task(job, param, file, exec_be, exec_bc, fs_be, fs_bc, name=""):
    logger.debug('')
    logger.debug("job %s" % job)
    logger.debug("file %s" % file)
    logger.debug("param %s" % param)
    logger.debug("exec_be %s" % exec_be)
    logger.debug("exec_bc %s" % exec_bc)
    logger.debug("fs_be %s" % fs_be)
    logger.debug("fs_bc %s" % fs_bc)
    

    param_scheme, param_uriparts = uriparse(param)
#    backend_scheme, backend_uriparts = uriparse(backendcredential.homedir)
    root, ext = splitext(file)
    
    # only make tasks for expected filetypes
    if ext.strip('.') in job.extensions:

        t = Task(job=job, status=settings.STATUS['ready'])
        t.save() # so task has id
        logger.debug('saved========================================')
        
        t.working_dir = create_uniq_dirname(job, t)
        
        fsscheme, fsbackend_parts = parse_url(job.fs_backend)
        execscheme, execbackend_parts = parse_url(job.exec_backend)
        
        t.command = job.command.replace("%", url_join(fsbackend_parts.path,t.working_dir, "input", file))
        t.name = name
        t.save()

        logger.info('Creating task for job id: %s using command: %s' % (job.id, t.command))
        logger.info('working dir is: %s' % (t.working_dir) )

        s = StageIn(task=t,
                    src="%s%s" % (param, file),
                    dst="%s://%s@%s%s" % (fsscheme,fsbackend_parts.username,fsbackend_parts.hostname, os.path.join(fsbackend_parts.path, t.working_dir, "input", file)),
                    order=0)
                    
        logger.debug("Stagein: %s <=> %s " % (s.src, s.dst))
        # TODO: Fix this whole dual backend bullshit!
        #destscheme = fs_bc.homedir_uri.split('//',1)[0]
        #dest = exec_be.uri.split('//',1)[1]
        
        #destcomposite = destscheme+"//"+dest
        
        #logger.info('destcomposite is: %s' % (destcomposite) )
        
        #s = StageIn(task=t,
                    #src=url_join(param, file),
                    #dst=url_join(exec_be.uri,t.working_dir, file),
                    #order=0)
        
        s.save()

def create_uniq_dirname(job, task):
    logger.debug('')
    return 'work-job%d-task%d/' % (job.id, task.id)
