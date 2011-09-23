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

from ExecConnector import ExecConnector, ExecutionError

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "local"

DEBUG = True

from twisted.web2 import http, responsecode, http_headers, stream

import shlex
import os
from utils.protocol import globus
import stackless
import tempfile

from utils.stacklesstools import sleep

from conf import config
from SubmissionTemplate import make_script

from twisted.internet import protocol
from twisted.internet import reactor

class BaseShellProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, stdin=None):
        self.stdin=stdin
        self.err = ""
        self.out = ""
        self.exitcode = None
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        if self.stdin:
            self.transport.write(self.stdin)
        self.transport.closeStdin()
        
    def outReceived(self, data):
        self.out += data
        if DEBUG:
            print "OUT:",data
        
    def errReceived(self, data):
        self.err += data
        if DEBUG:
            print "ERR:",data
    
    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        if DEBUG:
            print "Out lost"
        self.unifyLineEndings()
        
    def inConenctionLost(self):
        if DEBUG:
            print "In lost"
        self.unifyLineEndings()
        
    def errConnectionLost(self):
        if DEBUG:
            print "Err lost"
        self.unifyLineEndings()
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        if DEBUG:
            print "proc ended",self.exitcode
        self.unifyLineEndings()
        
    def unifyLineEndings(self):
        # try to unify the line endings to \n
        self.out = self.out.replace("\r\n","\n")
        self.err = self.err.replace("\r\n","\n")
        
    def isDone(self):
        return self.exitcode != None
        
    def isFailed(self):
        return self.isDone() and self.exitcode != 0

class BaseShell(object):
    def __init__(self):
        pass

    def _make_path(self):
        return "/usr/bin"    

    def _make_env(self, environ=None):
        """Return a custom environment for the specified cert file"""
        subenv = environ.copy() if environ!=None else os.environ.copy()
        return subenv    

    def execute(self, pp, command):
        """execute a command using a process protocol"""

        subenv = self._make_env()
        if DEBUG:
            print "env",subenv
            print "exec:",command
            print  [pp,
                                command[0],
                                command,
                                subenv,
                                self._make_path()]
            
            
        reactor.spawnProcess(   pp,
                                command[0],
                                command,
                                env=subenv,
                                path=self._make_path()
                            )
        return pp

class LocalRun(BaseShell):
    def run(self, certfile, remote_command="hostname", username="yabi", host="faramir.localdomain", working="/tmp", port="22", stdout="STDOUT.txt", stderr="STDERR.txt",password="",modules=[],streamin=None):
        """Spawn a process to run a remote ssh job. return the process handler"""
        subenv = self._make_env()
        
        if modules:
            remote_command = "&&".join(["module load %s"%module for module in modules]+[remote_command])
        
        if DEBUG:
            print "running local command:",remote_command
        
        return BaseShell.execute(self,BaseShellProcessProtocol(streamin),remote_command)

class LocalConnector(ExecConnector):    
    def run(self, yabiusername, creds, command, working, scheme, username, host, remoteurl, channel, submission, stdout="STDOUT.txt", stderr="STDERR.txt", walltime=60, memory=1024, cpus=1, queue="testing", jobtype="single", module=None):
        # preprocess some stuff
        modules = [] if not module else [X.strip() for X in module.split(",")]
        
        client_stream = stream.ProducerStream()
        channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))
        stackless.schedule()
        
        try:
            if DEBUG:
                print "LOCAL",command,"WORKING:",working,"CREDS passed in:%s"%(creds)    
            client_stream.write("Unsubmitted\n")
            stackless.schedule()
            
            client_stream.write("Pending\n")
            stackless.schedule()
            
            script_string = make_script(submission,working,command,modules,cpus,memory,walltime,yabiusername,username,host,queue, stdout, stderr)    
            
            if DEBUG:
                print "command:",command
                print "username:",username
                print "host:",host
                print "working:",working
                print "port:","22"
                print "stdout:",stdout
                print "stderr:",stderr
                print "modules:",modules
                print "submission script:",submission
                print "script string:",script_string
                
            pp = LocalRun().run(None,command,username,host,working,port="22",stdout=stdout,stderr=stderr,password=None, modules=modules)
            client_stream.write("Running\n")
            stackless.schedule()
            
            while not pp.isDone():
                stackless.schedule()
                
            if pp.exitcode==0:
                # success
                client_stream.write("Done\n")
                client_stream.finish()
                return
                
            # error
            if DEBUG:
                print "SSH Job error:"
                print "OUT:",pp.out
                print "ERR:",pp.err
            client_stream.write("Error\n")
            client_stream.finish()
            return
                    
        except Exception, ee:
            import traceback
            traceback.print_exc()
            client_stream.write("Error\n")
            client_stream.finish()
            return
        