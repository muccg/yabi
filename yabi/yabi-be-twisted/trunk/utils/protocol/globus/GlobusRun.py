# -*- coding: utf-8 -*-
import subprocess
import os

from BaseShell import BaseShell, BaseShellProcessProtocol

# This is our ProcessProtocol to handle the globusrun-ws programme
from twisted.internet import protocol
from twisted.internet import reactor
import re

DEBUG = False

re_jobid = re.compile(r"Job ID: uuid:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")
re_termtime = re.compile(r"Termination time: (\d{2}/\d{2}/\d{4} \d{2}:\d{2} \w+)")
re_currentjobstate = re.compile(r"Current job state: (\w+)")

class GlobusRunWSProcessProtocol(BaseShellProcessProtocol):
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
        
class GlobusStatusWSProcessProtocol(BaseShellProcessProtocol):
    def __init__(self):
        BaseShellProcessProtocol.__init__(self)
        self.jobstate = None
        
    def outReceived(self, data):
        self.out += data
        if DEBUG:
            print "OUT:",data
        
        if "job state" in self.out:
            result = re_currentjobstate.search(self.out)
            self.jobstate = result.group(1)
            
    
        
from twisted.internet import reactor

class GlobusRun(BaseShell):
    globusrun_ws = '/usr/local/globus/bin/globusrun-ws'
    
    def __init__(self):
        BaseShell.__init__(self)

    def run(self, certfile, rslfile, host="xe-gt4.ivec.org", factorytype="PBS"):
        """Spawn a process to run an xml job. return the process handler"""
        return BaseShell.execute(self,GlobusRunWSProcessProtocol, certfile,
            [
                self.globusrun_ws,
                "-F", host, 
                "-Ft", factorytype,
                "-submit",
                "-batch",
                "-job-description-file",
                rslfile,
            ]
        )
    
    def status(self, certfile, eprfile, host="xe-gt4.ivec.org", factorytype="PBS"):
        return BaseShell.execute(self, GlobusStatusWSProcessProtocol, certfile,
            [   self.globusrun_ws,
                "-F", host, "-Ft", factorytype,
                "-status",
                "-job-epr-file",
                eprfile,
            ]
        )
    

Run = GlobusRun()
