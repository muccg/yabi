# -*- coding: utf-8 -*-

import pickle
import os
import dircache
import stackless

from TaskTools import CloseConnections

class FileVersionMismatch(Exception): pass

class Tasklets(object):
    """This is a store for all the tasklets running in back end system. 
    From here they can be saved to disk and reloaded when the server is restarted
    """
    TASK_FILENAME_PREFIX = "taskjson-"
    
    def __init__(self):
        self.tasks = {}
        
    def add(self, task, taskid):
        self.tasks[taskid]=task
        
    def get(self, taskid):
        return self.tasks[taskid]
        
    def purge(self):
        """purge dead tasks from the list"""
        for id,task in self.tasks.iteritems():
            if task.finished():
                del self.tasks[id]
            elif task.errored():
                del self.tasks[id]
        
    def save(self, directory):
        for id,task in self.tasks.iteritems():
            # before we pickle it, if we are waiting on a connection in our stack frame, then set it to have failed
            # so that when we are resurrected in the future, the connection will immediately be marked as failed
            fname = os.path.join(directory,self.TASK_FILENAME_PREFIX+str(id))
            
            if not task.finished():
                self.save_task(task,fname)
            
    def save_task(self,task,filename):
        """Save the json and stage to a file"""
        with open(filename,"w") as fh:
            fh.write(pickle.dumps(("V1",task.__class__.__name__,task)))
  
    def load_task(self,filename):
        """Load the json from a file, create the right task object and return it"""
        from Task import NullBackendTask, MainTask
        
        with open(filename,'r') as fh:
            version, objname, task = pickle.loads(fh.read())
        
        #print "L:",task
        
        if version!="V1":
            raise FileVersionMismatch, "File Version Mismatch for %s"%(filename)
        
        # instantiate the object
        #task = locals()[objname]()
        #task.load_json(json, stage=stage)
        return task
            
    def load(self,directory):
        self.tasks={}
            
        for f in dircache.listdir(directory):
            if f.startswith(self.TASK_FILENAME_PREFIX):
                id = int(f[len(self.TASK_FILENAME_PREFIX):])
                path = os.path.join(directory,f)
                task = self.load_task(path)
                os.unlink(path)
                
                # lets try and start the task up
                runner = stackless.tasklet(task.run)
                runner.setup()
                runner.run()
                
                self.tasks[id]=task
                
                #print "task",task,"loaded"
           
    def debug(self):
        
        def dump_obj(obj):
            out = ""
            keys = dir(obj)
            #for key in [K for K in keys if not K.startswith("_")]:
            keys.remove("cstate")
            for key in keys:
                out+=key+": "+str(getattr(obj,key))+"\n"
            return out    
        
        output=""
        for task in self.tasks:
            section=str(task)+"\n"+("="*len(str(task)))+"\n"
            section+=dump_obj(task)
            section+="\n"
            
            output = "%s%s\n"%(output,section)
        return output
        
    def pickle(self):
        """ just try and serialise the objects"""
        self.save("/tmp")
        
    def get_all_blocked(self):
        """return a generator that iterates over all the tasks that are blocked"""
        return (self.tasks[X] for X in self.tasks.keys() if self.tasks.blocked())
    
tasklets = Tasklets()