# -*- coding: utf-8 -*-
"""Sun Grid Engine tools
"""
from twisted.internet import protocol
from twisted.internet import reactor

import re
import stackless
from tempfile import mktemp
import os
from utils.stacklesstools import sleep

from conf import config

QSUB_COMMAND = "/opt/torque/2.3.13/bin/qsub"             #-N job-101 /home/yabi/test-remote
QSTAT_COMMAND = "/opt/torque/2.3.13/bin/qstat"

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
        #print "OUT recv",data
        self.out += data
        
    def errReceived(self, data):
        #print "ERR recv",data
        self.err += data
            
    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        self.jobid = self.out.strip()
        #print "CONN LOST:",self.jobid
        return
        
        re_match = self.regexp.search(self.out)
        #print "OUT:",self.out
        #print "ERR:",self.err
        #print "RE_MATCH:",re_match
        if re_match:
            #print "Group",re_match.groups()
            jobid, jobname = re_match.groups()
            self.jobid = jobid
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
                                "-e",os.path.join(workingdir,stderr),
                                "-o",os.path.join(workingdir,stdout),
                                "-d",workingdir,
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

def qsub_backoff_generator():
    delay = 60.0
    yield delay
    
    while delay<3600.0:                      # while delay is less than an hour
        delay *= 2
        yield delay
        
    # exiting the generator means permanent error
    return

def qsub(jobname, command, user="yabi", workingdir="/home/yabi", stdout="STDOUT.txt", stderr="STDERR.txt", modules=[]):
    # use shlex to parse the command into executable and arguments
    #lexer = shlex.shlex(command, posix=True)
    #lexer.wordchars += r"-.:;/"
    #arguments = list(lexer)
     
     # make a temporary file to store the command in
    tempfile = mktemp(dir=config.config['backend']['temp'])
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
    
    retry=True
    delays = qsub_backoff_generator()
    while retry:
        # run the qsub process.
        pp = qsub_spawn(jobname,tempfile,user=user,workingdir=workingdir)
        
        while not pp.isDone():
            stackless.schedule()
            
        if pp.exitcode!=0:
            print "QSUB ERROR CODE:",pp.exitcode
            
            # deal with qstat failures
            if pp.exitcode==171 and "Invalid credential" in pp.err:
                print "Invalid credential temporary error"
                # backoff
                sleep(20.0)
                
            elif "Maximum number of jobs already in queue" in pp.err:
                # backoff
                try:
                    delay = delays.next()
                    print "Backing off",delay
                    sleep(delay)
                except StopIteration:
                    raise ExecutionError("torque qsub is reporting too many jobs in the queue for this user, and after backing off and retrying a number of times we've given up trying!")
            else:
                err = pp.err
                print "QSUB ERROR:",err
                from ex.connector.ExecConnector import ExecutionError
                raise ExecutionError(err)
        else:
            retry = False
    
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
    regexp = re.compile(r"""\s+(\w+)                    # key
                            \s*=\s*                     # =
                            (.+)\s*$                   # value
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
        #print "out:",data
        self.out += data
        
    def errReceived(self, data):
        #print "====> Qstat err:",data
        self.err += data
            
    def outConnectionLost(self):
        #print "lost!"
        # stdout was closed. this will be our endpoint reference
        key = "STDOUT"
        self.data = {key:""}
        for line in self.out.split("\n"):
            if line.startswith(' '):
                re_match = self.regexp.search(line)
                #print "RE_MATCH:",re_match
                if re_match:
                    key,value = re_match.groups()
                    #print "key",key,"value",value
                    self.data[key] = value
            else:
                self.data[key]+=line+"\n"
                
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        
    def isDone(self):
        return self.exitcode != None
    
def qstat_spawn(jobid, user="yabi"):
    """return the status of a running job via qstat
    /opt/sge/6.2u3/bin/lx24-amd64/qstat -u yabi
    """
    subenv = os.environ.copy()
    pp = QstatProcessProtocol()
    
    command = [
                                QSTAT_COMMAND,
                                "-f","-1",
                                jobid
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

from ex.connector.ExecConnector import ExecutionError
def qstat(jobid, user="yabi"):
    # run the qsub process.
    pp = qstat_spawn(jobid, user)
    
    while not pp.isDone():
        stackless.schedule()
        
    if pp.exitcode!=0:
        err = pp.err
        print "QSTAT EXIT CODE",pp.exitcode
        raise ExecutionError(err)

    jobs = {}
    jobs[jobid] = pp.data
    return jobs
    