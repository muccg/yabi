from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog

def walk(workflow):

    for job in workflow.job_set.all().order_by("order"):

        #check job status
        process_job(job)



def must_be_ready(func):

    def ready(job):
        print "Checking the job is ready to run."
        func(job)

    return ready


def gather_inputs(func):

    def gather(job):
        print "Gathering the inputs."
        func(job)

    return gather


def prepare_tasks(func):

    def prepare(job):
        print "Preparing the tasks."
        func(job)

    return prepare



@must_be_ready
@gather_inputs
@prepare_tasks
def process_job(job):
    print "Setting job status to run"
    print "------------------------------"
    job.status = "run_me"
    job.save()




