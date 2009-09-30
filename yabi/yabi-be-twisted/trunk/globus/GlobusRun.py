import subprocess
import os

# This is our ProcessProtocol to handle the globusrun-ws programme
from twisted.internet import protocol
from twisted.internet import reactor
import re

re_jobid = re.compile(r"Job ID: uuid:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")
re_termtime = re.compile(r"Termination time: (\d{2}/\d{2}/\d{4} \d{2}:\d{2} \w+)")
re_currentjobstate = re.compile(r"Current job state: (\w+)")

class GlobusRunWSProcessProtocol(protocol.ProcessProtocol):
    def __init__(self):
        self.err = ""
        self.out = ""
        self.exitcode = None
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        self.transport.closeStdin()
        
    def outReceived(self, data):
        self.out += data
        
    def errReceived(self, data):
        self.err += data
       
        # see if we are done yet:
        if "Job ID" in self.err  and "Done" in self.err and "Termination time" in self.err:
            result = re_jobid.search(self.err)
            self.job_id = result.group(1)
            
            result = re_termtime.search(self.err)
            self.termtime = result.group(1)
            
    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        self.epr = self.out
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        
    def isDone(self):
        return self.exitcode != None
        
class GlobusStatusWSProcessProtocol(protocol.ProcessProtocol):
    def __init__(self):
        self.err = ""
        self.out = ""
        self.exitcode = None
        self.jobstate = None
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        self.transport.closeStdin()
        
    def outReceived(self, data):
        self.out += data
        
        if "job state" in self.out:
            result = re_currentjobstate.search(self.out)
            self.jobstate = result.group(1)
        
    def errReceived(self, data):
        self.err += data
            
    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        self.epr = self.out
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        
    def isDone(self):
        return self.exitcode != None
from twisted.internet import reactor

class GlobusRun(object):
    globusrun_ws = '/usr/local/globus/bin/globusrun-ws'
    
    def __init__(self):
        pass

    def _make_env(self, certfile):
        """Return a custom environment for the specified cert file"""
        subenv = os.environ.copy()
        subenv['X509_USER_PROXY'] = certfile
        
        return subenv
    
    def _make_path(self):
        return "/usr/local/globus/bin"

    def run(self, certfile, rslfile, host="xe-ng2.ivec.org", factorytype="PBS"):
        """Spawn a process to run an xml job. return the process handler"""
        print certfile, rslfile, host, factorytype
        subenv = self._make_env(certfile)
        
        pp = GlobusRunWSProcessProtocol()
        reactor.spawnProcess(   pp,
                                self.globusrun_ws, 
                                args=[
                                    self.globusrun_ws,
                                    "-F", host, 
                                    "-Ft", factorytype,
                                    "-submit",
                                    "-batch",
                                    "-job-description-file",
                                    rslfile,
                                ],
                                env=subenv,
                                path=self._make_path(),
                                #uid=uid,
                                #gid=gid,
                                #usePTY=usePTY,
                                #childFDs=childFDs 
                            )

        

        #set_file_unbuffered(proc.stdout)
        return pp
    
    def status(self, certfile, eprfile, host="xe-ng2.ivec.org", factorytype="PBS"):
        subenv = self._make_env(certfile)
        
        pp = GlobusStatusWSProcessProtocol()
        reactor.spawnProcess(   pp,
                                self.globusrun_ws,
                                [   self.globusrun_ws,
                                    "-F", host, "-Ft", factorytype,
                                    "-status",
                                    "-job-epr-file",
                                    eprfile,
                                ],
                                env=subenv,
                                path=self._make_path()
                            )
        
        return pp

