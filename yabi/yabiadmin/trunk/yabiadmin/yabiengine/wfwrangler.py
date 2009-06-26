from django.conf import settings
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog
from yabiadmin.yabiengine.YabiJobException import YabiJobException


def walk(workflow):

    for job in workflow.job_set.all().order_by("order"):

        try:

            #check job status
            prepare_dependencies(job)
            prepare_files(job)
            prepare_tasks(job)
            process_job(job)

        except (YabiJobException):
            continue




def prepare_dependencies(job):
    print "Checking the job is ready to run."
    print job.status_dependencies_ready()

def prepare_files(job):
    print "Gathering the files."
    print job.status_files_ready()    

def prepare_tasks(job):
    print "Preparing the tasks."
    print job.status_tasks_ready()



def process_job(job):
    print "Setting job status to run"
    print "------------------------------"
    print job.status_complete()
    job.status = "run_me"
    job.save()




