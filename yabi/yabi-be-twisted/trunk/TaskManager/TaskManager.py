from twisted.web import client
from twisted.internet import reactor
import json
import stackless
import weakref
import random
import os

from TaskTools import Copy, RCopy, Sleep, Log, Status, Exec, Mkdir, Rm, List, UserCreds, GetFailure

class TaskManager(object):
    TASK_HOST = "localhost"
    TASK_PORT = 8000
    TASK_URL = "http://%s:%d/yabiadmin/engine/task/"%(TASK_HOST,TASK_PORT)
    
    JOBLESS_PAUSE = 5.0                 # wait this long when theres no more jobs, to try to get another job
    JOB_PAUSE = 0.0                     # wait this long when you successfully got a job, to get the next job
    
    WORKING_DIR_CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"
    WORKING_DIR_LEN = 16                # length of filename for working directory
    
    def __init__(self):
        self.pausechannel = stackless.channel()
    
        self._tasks=weakref.WeakKeyDictionary()                  # keys are weakrefs. values are remote working directory
    
    def make_unique_name(self, prefix="work-",suffix=""):
        """make a unique name for the working directory"""
        makename = lambda: prefix+"".join([random.choice(self.WORKING_DIR_CHARS) for num in range(self.WORKING_DIR_LEN)])+suffix
        
        name = makename()
        while name in self._tasks.values():
            name = makename()
            
        return name
    
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
        
        self._tasks[tasklet] = None
        
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
        print "=========JSON============="
        print task
        print "=========================="
        
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
           
            print "TASK[%s]: Copy %s to %s Success!"%(taskid,src_url,dst_url)
        
        # get our credential working directory. We lookup the execution backends auth proxy cache, and get the users home directory from that
        # this comes from their credentials.
        usercreds = UserCreds(task['yabiusername'],task['exec']['backend'])
        homedir = usercreds['homedir']
                
        # make our working directory
        status("mkdir")
        dirname = self.make_unique_name()
        fulldirname = os.path.join(homedir,dirname)
        print "Making directory",fulldirname
        self._tasks[stackless.getcurrent()]=dirname
        try:
            Mkdir(fulldirname)
        except GetFailure, error:
            # error making directory
            print "TASK[%s]:Mkdir failed!"%(taskid)
            status("error")
            log("Making working directory of %s failed: %s"%(dirname,error))
            return 
        
        # we need to turn our backend path into a full remote fs path
        # get our backend
        from FSCache import FSCache
        fs_bend_name = fulldirname.split("/")[0]
        fs_bend = FSCache[fs_bend_name]
        bend_path = fs_bend.PrefixRemotePath(fulldirname)
         
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
            Exec(task['exec']['backend'], task['yabiusername'], command=task['exec']['command'], directory=bend_path, stdout="STDOUT.txt",stderr="STDERR.txt", callbackfunc=_task_status_change)                # this blocks untill the command is complete.
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
        
        # recursively copy the working directory to our stageout area
        log("Staging out remote %s to %s..."%(bend_path,task['stageout']))
        
        # make sure we have the stageout directory
        log("making stageout directory %s"%task['stageout'])
        try:
            Mkdir(task['stageout'])
        except GetFailure, error:
            pass
        
        try:
            RCopy(fulldirname+"/",task['stageout'])
            log("Files successfuly staged out")
        except GetFailure, error:
            # error executing
            print "TASK[%s]: Stageout failed!"%(taskid)
            status("error")
            log("Staging out remote %s to %s failed... %s"%(bend_path,task['stageout'],error))
            return              # finish task
        
        # cleanup
        status("cleaning")
        log("Cleaning up job...")
        
        for copy in task['stagein']:
            dst_url = "%s/%s%s"%(copy['dstbackend'],task['yabiusername'],copy['dstpath'])
            log("Deleting %s..."%(dst_url))
            try:
                Rm(dst_url, recurse=True)
            except GetFailure, error:
                # error copying!
                print "TASK[%s]: Delete %s Error!"%(dst_url)
                status("error")
                log("Deleting %s failed: %s"%(dst_url, error))
                return              # finish task
            
        # cleanup working dir
        try:
            Rm(fulldirname, recurse=True)
            log("Stageout directory %s deleted"%fulldirname)
        except GetFailure, error:
            # error copying!
            print "TASK[%s]: Delete %s Error!"%(fulldirname)
            status("error")
            log("Deleting %s failed: %s"%(fulldirname, error))
            return  
        
        log("Job completed successfully")
        status("complete")
        
        