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
import subprocess
import os

from BaseShell import BaseShell, BaseShellProcessProtocol

# This is our ProcessProtocol to handle the globusrun-ws programme
from twisted.internet import protocol
from twisted.internet import reactor
import re

from conf import config

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
        globus_command = [
                self.globusrun_ws,
                "-F", host, 
                "-Ft", factorytype,
                "-submit",
                "-batch",
                "-job-description-file",
                rslfile,
            ]
        
        # hande log setting
        if config.config['execution']['logcommand']:
            print "Globus attempting submission command: "+ (" ".join(globus_command))
            
        if config.config['execution']['logscript']:
            print "Globus submission script:"
            with open(rslfile) as fh:
                print fh.read()
                
        return BaseShell.execute(self,GlobusRunWSProcessProtocol, certfile, globus_command )
    
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
