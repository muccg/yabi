from twisted.web import client
from twisted.internet import reactor
import json
import stackless

from TaskTools import Copy, Sleep, Log, Status, Exec

class TaskManager(object):
    TASK_HOST = "localhost"
    TASK_PORT = 8000
    TASK_URL = "http://%s:%d/yabiadmin/engine/task/"%(TASK_HOST,TASK_PORT)
    
    JOBLESS_PAUSE = 5.0                 # wait this long when theres no more jobs, to try to get another job
    JOB_PAUSE = 0.0                     # wait this long when you successfully got a job, to get the next job
    
    def __init__(self):
        self.pausechannel = stackless.channel()
    
    def start(self):
        """Begin the task manager by going and getting a task"""
        self.runner_thread = stackless.tasklet(self.runner)
        self.runner_thread.setup()
        self.runner_thread.run()
        
    def runner(self):
        """The green task that starts up jobs"""
        while True:                 # do forever.
            self.get_next_task()
            
            # wait for this task to start or fail
            Sleep(self.pausechannel.receive())
        
    def start_task(self, data):
        taskdescription=json.loads(data)
        
        print "starting task:",taskdescription['taskid']
        
        # make the task and run it
        tasklet = stackless.tasklet(self.task)
        tasklet.setup(taskdescription)
        tasklet.run()
        
        # task successfully started. Lets try and start anotherone.
        self.pausechannel.send(self.JOB_PAUSE)
         
         
    def get_next_task(self):
        host,port = "localhost",8000
        useragent = "YabiFS/0.1"
        
        factory = client.HTTPClientFactory(
            self.TASK_URL,
            agent = useragent
            )
        reactor.connectTCP(host, port, factory)
        
        # now if the page fails for some reason. deal with it
        def _doFailure(data):
            print "No more jobs. Sleeping for",self.JOBLESS_PAUSE
            # no more tasks. we should wait for the next task.
            self.pausechannel.send(self.JOBLESS_PAUSE)
            
        return factory.deferred.addCallback(self.start_task).addErrback(_doFailure)
        
    def task(self,task, taskrunner=None):
        print "JSON:",task
        
        taskid = task['taskid']
        if not taskrunner:
            taskrunner=self.task_mainline
        try:
            return taskrunner(task)
        except Exception, exc:
            print "TASK[%s] raised uncaught exception: %s"%(taskid,exc)
            Log(task['errorurl'],"Raised uncaught exception: %s"%(exc))
            Status(task['statusurl'],"error")
            import traceback
            traceback.print_exc()
        
    def task_mainline(self, task):
        """Our top down greenthread code"""
        # stage in file
        taskid = task['taskid']
        
        statusurl = task['statusurl']
        errorurl = task['errorurl']
        
        # shortcuts for our status and log calls
        status = lambda x: Status(statusurl,x)
        log = lambda x: Log(errorurl,x)
        
        status("stagein")
        for copy in task['stagein']:
            src_url = "%s/%s%s"%(copy['srcbackend'],task['yabiusername'],copy['srcpath'])
            dst_url = "%s/%s%s"%(copy['dstbackend'],task['yabiusername'],copy['dstpath'])
            log("Copying %s to %s..."%(src_url,dst_url))
            try:
                Copy(src_url,dst_url)
                log("Copying %s to %s Success"%(src_url,dst_url))
            except GetFailure, error:
                # error copying!
                print "TASK[%s]: Copy %s to %s Error!"%(taskid,src_url,dst_url)
                status("error")
                log("Copying %s to %s failed: %s"%(src_url,dst_url, error))
                return              # finish task
            
            log("Copying %s to %s Success"%(src_url,dst_url))
            
            print "TASK[%s]: Copy %s to %s Success!"%(taskid,src_url,dst_url)
        
        # now we are going to run the job
        status("exec")
        
        # callback for job execution status change messages
        def _task_status_change(line):
            """Each line that comes back from the webservice gets passed into this callback"""
            line = line.strip()
            print "_task_status_change(",line,")"
            log("Remote execution backend changed status to: %s"%(line))
            status("exec:%s"%(line.lower()))
        
        # submit the job to the execution middle ware
        log("Submitting to %s command: %s"%(task['exec']['backend'],task['exec']['command']))
        
        try:
            Exec(task['exec']['backend'], task['yabiusername'], command=task['exec']['command'], directory="/tmp", callbackfunc=_task_status_change)                # this blocks untill the command is complete.
            log("Execution finished")
        except GetFailure, error:
            # error executing
            print "TASK[%s]: Execution failed!"%(taskid)
            status("error")
            log("Execution of %s on %s failed: %s"%(task['exec']['command'],task['exec']['backend'],error))
            return              # finish task
        
        # stageout
        log("Staging out results")
        status('stageout')
        
        