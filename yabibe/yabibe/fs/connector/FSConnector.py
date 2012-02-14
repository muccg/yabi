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

class NotImplemented(Exception):
    """Exception to mark methods that haven't been overridden... yet..."""
    pass

class FSConnector(object):
    """Base class for a filesystem connector"""
    def __init__(self):
        self.childenv = {}
   
    def SetEnvironment(self, env):
        """Pass in the environment setup you want any child processes to inherit"""
        self.childenv = env.copy()
    
    def GetReadFifo(self, host=None, username=None, path=None, filename=None, fifo=None, yabiusername=None, creds={}):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        """
        raise NotImplemented("GetReadFifo not implemented")
            
    def GetWriteFifo(self, host=None, username=None, path=None, filename=None, fifo=None, yabiusername=None, creds={}):
        """sets up the chain needed to setup a write fifo to a remote path as a certain user.
        """
        raise NotImplemented("GetWriteFifo not implemented")
        
    def ls(self, host, username, path, yabiusername=None, recurse=False, culldots=True, creds={}):
        raise NotImplemented("ls not implemented")
        
    def mkdir(self, host, username, path, yabiusername=None, creds={}):
        """mkdir command. Uses self.path. If path is passed in (not None), then it overrides the request.path, and we go make this path instead.
        remember path must be a list.
        """
        raise NotImplemented("mkdir not implemented")

    def rm(self, host, username, path, yabiusername=None, recurse=False, creds={}):
        """If path is passed in, remove this remote path instead of self.path (like MKDIR)"""
        raise NotImplemented("rm not implemented")
    
    def NonFatalRetryGenerator(self):
        """This returns a generator that generates the retry delays for a non fatal error. Here you can tailor the retry
        timeouts for this particular backend. To make it retry forever, make an infinite generator. When the generator 
        finally exits, the error is raised. The default is an exponential backoff
        """
        NUM_RETRIES = 5                     # number of retries
        delay = 5.0                         # first delay
        for i in range(NUM_RETRIES):
            yield delay
            delay*=2.                       # double each time
            
    # In order to identify a non fatal copy failure, we search for each of these phrases in stdout/stderr of the copy classes.
    # comparison is case insensitive
    NonFatalKeywords = [ "connection refused", "connection reset by peer" ]                 # "broken pipe"?
    