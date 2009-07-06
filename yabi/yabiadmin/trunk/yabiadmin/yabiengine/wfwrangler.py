import logging
logger = logging.getLogger('yabiengine')
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog
from yabiadmin.yabiengine.YabiJobException import YabiJobException
from yabiadmin.yabiengine import backend
from django.utils import simplejson as json


def walk(workflow):

    for job in workflow.job_set.all().order_by("order"):
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
            logger.info(e.message)
            continue


def check_dependencies(job):
    """Check each of the dependencies in the jobs command params.
    Start with a ready value of True and if any of the dependecies are not ready set ready to False.
    If dependencies are all met change job status to settings.STATUS['dependencies_ready']
    """
    logger.info('Check dependencies for jobid: %s...' % job.id)

    try:
        for param in eval(job.commandparams):

            if param.startswith("yabi://"):
                logger.info('Evaluating param: %s' % param)
                workflowid, jobid = param[7:].split("/")
                param_job = Job.objects.get(workflow__id=workflowid, id=jobid)
                if param_job.status != settings.STATUS["complete"]:
                    raise YabiJobException("Job command parameter not complete. Job:%s Param:%s" % (job.id, param))

    except ObjectDoesNotExist, e:
        raise YabiJobException('Error with job param: %s' % e.message)


def prepare_tasks(job):
    logger.info('Preparing tasks for jobid: %s...' % job.id)

    input_files = []

    for param in eval(job.commandparams):

        if param.startswith("yabi://"):
            logger.info('Processing uri %s' % param)
            files = [] # query backend with uri
            for file in files:
                input_files.append(file)

        if param.startswith("file://") and param.endswith("/"):
            logger.info('Processing uri %s' % param)

            results = json.loads(backend.ls(param))

            for key in results.keys():
                for file in results[key]["files"]:
                    input_files.append(file[0])                    

            files = [] # query backend with uri
            for file in files:
                input_files.append(file)

        if param.startswith("file://"):
            logger.info('Processing uri %s' % param)            
            input_files.append(param)

    for file in input_files:
        taskcommand = job.command.replace("%", file)
        logger.info('Creating task for job id: %s using command: %s' % (job.id, taskcommand))
        t = Task(job=job, command=taskcommand, status="ready")
        t.save()
        

def prepare_job(job):
    logger.info('Setting job id %s to ready' % job.id)                
    job.status = settings.STATUS["ready"]
    job.save()


