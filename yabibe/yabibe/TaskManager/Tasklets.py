# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
# -*- coding: utf-8 -*-

import pickle
import os
import dircache
import gevent

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
                try:
                    task = self.load_task(path)
                    os.unlink(path)
                
                    # lets try and start the task up
                    runner = gevent.spawn(task.run)
                    
                    self.tasks[id]=task
                except EOFError, eofe:
                    print "WARNING: damaged task file: %s"%path
                    
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