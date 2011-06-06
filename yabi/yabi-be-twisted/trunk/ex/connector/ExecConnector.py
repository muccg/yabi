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
"""Base class for FSConnector"""

import pickle, os

class NotImplemented(Exception):
    """Exception to mark methods that haven't been overridden... yet..."""
    pass

class ExecutionError(Exception):
    pass

class ExecConnector(object):
    """Base class for a filesystem connector"""
    
    def __init__(self):
        self.childenv = {}
    
        
        self._running = {}
        
    def add_running(self, rid, details):
        self._running[rid]=details.copy()

    def get_running(self, rid):
        return self._running[rid]
        
    def update_running(self, rid, updatehash):
        self._running[rid].update(updatehash)
        
    def del_running(self, rid):
        del self._running[rid]

    def get_all_running(self):
        return self._running
        
    def save_running(self, filename):
        """save the running job details to a file so we can restore the details we need on startup to resume connections to tasks"""
        with open(filename,'wb') as fh:
            fh.write(pickle.dumps(self._running))
    
    def load_running(self, filename):
        """return the running set details from a file"""
        with open(filename,'rb') as fh:
            self._running = pickle.loads(fh.read())
    
    def shutdown(self, directory):
        print self.__class__.__name__+"::shutdown(",directory,")"
        self.save_running(os.path.join(directory,"exec-"+self.__class__.__name__))        
        
    def startup(self, directory):
        print self.__class__.__name__+"::startup(",directory,")"
        filename = os.path.join(directory,"exec-"+self.__class__.__name__)
        if os.path.exists(filename):
            self.load_running(filename)        
    
    #def run(self, yabiusername, command, working, scheme, username, host, channel, stdout="STDOUT.txt", stderr="STDERR.txt", maxWallTime=60, maxMemory=1024, cpus=1, queue="testing", jobType="single", module=None, **creds):
    def run(self, *args, **kwargs):
        """Run a job on a backend. extra params can be passed in that are specific to a backend. They should all have defaults if ommitted
        
        command is the command to run
        working is the working directory
        address is the host on which to run the command
        
        callback is a callable that is called with the status changes for the running job
        
        """
        #print "The run method for this backend is not implemented"
        raise NotImplemented("The run method for this backend is not implemented")
    
    def SetEnvironment(self, env):
        """Pass in the environment setup you want any child processes to inherit"""
        self.childenv = env.copy()
        