# -*- coding: utf-8 -*-
"""Sun Grid Engine tools
"""
from twisted.internet import protocol
from twisted.internet import reactor

import re
import stackless
import shlex
from tempfile import mktemp
import os
import pwd

QSUB_COMMAND = "/opt/sge/6.2u3/bin/lx24-amd64/qsub"             #-N job-101 /home/yabi/test-remote
QSTAT_COMMAND = "/opt/sge/6.2u3/bin/lx24-amd64/qstat"

SUDO = "/usr/bin/sudo"
USE_SUDO = True                          

DEBUG = False

class QsubProcessProtocol(protocol.ProcessProtocol):
    """ Job returns 'Your job 10 ("jobname") has been submitted'
    """
    regexp = re.compile(r'Your job (\d+) \("(\w+)"\) has been submitted')
    
    def __init__(self):
        self.err = ""
        self.out = ""
        self.exitcode = None
        self.jobid = None
        self.jobname = None
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        self.transport.closeStdin()
        
    def outReceived(self, data):
        self.out += data
        
    def errReceived(self, data):
        self.err += data
            
    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        re_match = self.regexp.search(self.out)
        #print "OUT:",self.out
        #print "ERR:",self.err
        #print "RE_MATCH:",re_match
        if re_match:
            #print "Group",re_match.groups()
            jobid, jobname = re_match.groups()
            self.jobid = int(jobid)
            self.jobname = jobname
            #print "jobid=",jobid
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        
    def isDone(self):
        return self.exitcode != None
    
def qsub_spawn(jobname, commandfile, user="yabi", workingdir="/home/yabi", stdout="STDOUT.txt", stderr="STDERR.txt", modulelist=[]):
    """Spawn a process to run an xml job. return the process handler"""
    subenv = os.environ.copy()
    pp = QsubProcessProtocol()
    
    command = [
                                QSUB_COMMAND,
                                "-N",
                                jobname,
                                "-e",stderr,
                                "-o",stdout,
                                "-wd",workingdir,
                                commandfile
                            ]
    
    if USE_SUDO:
        command = [             SUDO,
                                "-u",
                                user
                  ] + command
                                
    
    if DEBUG:
        print command
    reactor.spawnProcess(   pp,
                            command[0], 
                            args=command,
                            env=subenv
                        )

    return pp

def qsub(jobname, command, user="yabi", workingdir="/home/yabi", stdout="STDOUT.txt", stderr="STDERR.txt", modules=[]):
    # use shlex to parse the command into executable and arguments
    #lexer = shlex.shlex(command, posix=True)
    #lexer.wordchars += r"-.:;/"
    #arguments = list(lexer)
     
     # make a temporary file to store the command in
    tempfile = mktemp()
    temp=open(tempfile,'w+b')
    
    # write module load lines
    for module in modules:
        # assert the module name is sanity
        assert " " not in module
        temp.write("module load %s\n"%(module))
    
    temp.write(command)
    temp.write("\n")
    temp.close()
   
    # user we are submitting as needs to be able to read the file
    os.chmod(tempfile, 0604)
    
    # run the qsub process.
    pp = qsub_spawn(jobname,tempfile,user=user,workingdir=workingdir)
    
    while not pp.isDone():
        stackless.schedule()
        
    if pp.exitcode!=0:
        err = pp.err
        from ex.connector.ExecConnector import ExecutionError
        raise ExecutionError(err)
    
    # delete temp?
    os.unlink(tempfile)
    
    return pp.jobid

class QstatProcessProtocol(protocol.ProcessProtocol):
    """ Job returns 'Your job 10 ("jobname") has been submitted'
    
job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID 
-----------------------------------------------------------------------------------------------------------------
    12 0.00000 job-101    yabi         qw    10/13/2009 10:42:52                                    1        

    """
    # match line of form  "   12 0.00000 job-101    yabi         qw    10/13/2009 10:42:52                                    1        "
    regexp = re.compile(r"""\s+(\d+)                    # job-ID
                            \s+([\d.]+)                 # prior
                            \s+([\w\-\d_]+)             # name
                            \s+(\w+)                    # user
                            \s+(\w+)                    # state
                            \s+([\d/]+)                 # submit/start
                            \s+(\d+:\d+:\d+)            # at
                            \s+([\w\d\-@.]*)            # submit host (optional)
                            \s+(\d+)\s+$                # everything else on the line
                        """, re.VERBOSE)
    
    def __init__(self):
        self.err = ""
        self.out = ""
        self.exitcode = None
        
        # where we store the data gathered from the process
        self.jobs = {}
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        self.transport.closeStdin()
        
    def outReceived(self, data):
        self.out += data
        
    def errReceived(self, data):
        self.err += data
            
    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        for line in self.out.split("\n"):
            re_match = self.regexp.search(line)
            #print "RE_MATCH:",re_match
            if re_match:
                jobid, prior, name, user, status, submit, at, host, rest = re_match.groups()
                jobid=int(jobid)
                self.jobs[jobid] = dict(name=name,user=user,status=status,submit=submit,at=at,rest=rest,host=host,prior=prior)
                if DEBUG:
                    print self.jobs[jobid]
                #print "id",jobid
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        
    def isDone(self):
        return self.exitcode != None
    
def qstat_spawn(user="yabi"):
    """return the status of a running job via qstat
    /opt/sge/6.2u3/bin/lx24-amd64/qstat -u yabi
    """
    subenv = os.environ.copy()
    pp = QstatProcessProtocol()
    
    if DEBUG:
        print [
                                QSTAT_COMMAND,
                                "-u",
                                user
                            ]
    
    reactor.spawnProcess(   pp,
                            QSTAT_COMMAND, 
                            args=[
                                QSTAT_COMMAND,
                                "-u",
                                user
                            ],
                            env=subenv
                        )

    return pp

def qstat(user="yabi"):
    # run the qsub process.
    pp = qstat_spawn(user)
    
    while not pp.isDone():
        stackless.schedule()
        
    if pp.exitcode!=0:
        err = pp.err
        from ex.connector.ExecConnector import ExecutionError
        raise ExecutionError(err)
    
    return pp.jobs
    
