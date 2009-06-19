from twisted.web import client
from twisted.internet import reactor
import json
import stackless

from TaskTools import Copy

class TaskManager(object):
    TASK_HOST = "localhost"
    TASK_PORT = 8000
    TASK_URL = "http://%s:%d/yabiadmin/engine/task/"%(TASK_HOST,TASK_PORT)
    
    def __init__(self):
        pass
    
    def start(self):
        """Begin the task manager by going and getting a task"""
        self.get_next_task()
        
    def start_task(self, data):
        taskdescription=json.loads(data)
        
        print "starting task:",taskdescription['taskid']
        
        # make the task and run it
        tasklet = stackless.tasklet(self.task)
        tasklet.setup(taskdescription)
        tasklet.run()
         
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
            print "Failed:",factory,":",type(data),data.__class__
            print data
            
        return factory.deferred.addCallback(self.start_task).addErrback(_doFailure)
        
    def task(self, task):
        """Our top down greenthread code"""
        # stage in file
        taskid = task['taskid']
        
        for copy in task['stagein']:
            src_url = "%s/%s%s"%(copy['srcbackend'],task['yabiusername'],copy['srcpath'])
            dst_url = "%s/%s%s"%(copy['dstbackend'],task['yabiusername'],copy['dstpath'])
            if not Copy(src_url,dst_url):
                # error copying!
                print "TASK[%s]: Copy %s to %s Error!"%(taskid,src_url,dst_url)
                return                      # finish task
            else:
                print "TASK[%s]: Copy %s to %s Success!"%(taskid,src_url,dst_url)
            
        for wait in range(100):
            print "waiting",wait
            for i in range(100):
                stackless.schedule()