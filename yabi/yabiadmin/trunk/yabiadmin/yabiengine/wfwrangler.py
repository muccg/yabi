import logging
logger = logging.getLogger('yabiengine')
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog, StageIn
from yabiadmin.yabmin.models import Backend, BackendCredential
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

    # get the backend for this job
    b = Backend.objects.get(name=job.exec_backend)
    bc = BackendCredential.objects.get(backend=b, credential__user=job.workflow.user)





    for param in eval(job.commandparams):

        if param.startswith("yabi://"):
            logger.info('Processing uri %s' % param)
            files = [] # query backend with uri
            for file in files:
                input_files.append(file)


        # uris ending with a / on the end of the path are directories
        if param.startswith("file://") and param.endswith("/"):
            logger.info('Processing uri %s' % param)

            results = json.loads(backend.ls(param))

            for key in results.keys():
                for file in results[key]["files"]:



                    taskcommand = job.command.replace("%", "%s%s%s" % (b.path, backend.uri2homedir(bc.homedir),file[0]))
                    logger.info('Creating task for job id: %s using command: %s' % (job.id, taskcommand))
                    t = Task(job=job, command=taskcommand, status="ready")
                    t.save()

                    s = StageIn(task=t,
                                src_backend=backend.scheme(param),
                                src_path="%s%s" % (backend.uri2homedir(param), file[0]), # change the name of uri2homedir
                                dst_backend=job.fs_backend,
                                dst_path="%s%s" % (backend.uri2homedir(bc.homedir), file[0]),
                                order=0)
                    s.save()









        if param.startswith("file://"):
            logger.info('Processing uri %s' % param)            
            input_files.append(param)



def prepare_job(job):
    logger.info('Setting job id %s to ready' % job.id)                
    job.status = settings.STATUS["ready"]
    job.save()


