# -*- coding: utf-8 -*-
"""Sun Grid Engine tools
"""
from twisted.internet import protocol
from twisted.internet import reactor

import re
import stackless
from tempfile import mktemp
import os

from conf import config

QSUB_COMMAND = "/opt/sge/6.2u3/bin/lx24-amd64/qsub"             #-N job-101 /home/yabi/test-remote
QSTAT_COMMAND = "/opt/sge/6.2u3/bin/lx24-amd64/qstat"
QACCT_COMMAND = "/opt/sge/6.2u3/bin/lx24-amd64/qacct"

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
                jobid=jobid
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

class QstatVerboseProcessProtocol(protocol.ProcessProtocol):
    """handle the qstat -u user -f -j jobid"""

    def __init__(self, jobs, jobid):
        self.err = ""
        self.out = ""
        self.exitcode = None

        # where we store the data gathered from the process
        self.jobs = jobs
        self.jobid = jobid

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
            if ':' in line:
                key,val = line.split(':',1)
                val = val.strip()
                key = key.strip()

                self.jobs[self.jobid][key] = val

    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode

    def isDone(self):
        return self.exitcode != None

def qstat_verbose_spawn(jobs,user,jobid):
    """return the status of a running job via qstat
    /opt/sge/6.2u3/bin/lx24-amd64/qstat -u yabi
    """
    subenv = os.environ.copy()
    pp = QstatVerboseProcessProtocol(jobs,jobid)

    if DEBUG:
        print [
                                QSTAT_COMMAND,
                                "-u",
                                user,
                                "-f",
                                "-j",
                                jobid
                            ]

    reactor.spawnProcess(   pp,
                            QSTAT_COMMAND,
                            args=[
                                QSTAT_COMMAND,
                                "-u",
                                user,
                                "-f",
                                "-j",
                                jobid
                            ],
                            env=subenv
                        )

    return pp


class QacctProcessProtocol(protocol.ProcessProtocol):
    """ qacct returns 
    
==============================================================
qname        all.q               
hostname     yabi-e-dev.localdomain
group        tech                
owner        ahunter             
project      NONE                
department   defaultdepartment   
jobname      jobname             
jobnumber    1306                
taskid       undefined
account      sge                 
priority     0                   
qsub_time    Tue Apr 13 13:50:19 2010
start_time   Tue Apr 13 13:54:21 2010
end_time     Tue Apr 13 13:54:21 2010
granted_pe   NONE                
slots        1                   
failed       0    
exit_status  0                   
ru_wallclock 0            
ru_utime     0.060        
ru_stime     0.080        
ru_maxrss    0                   
ru_ixrss     0                   
ru_ismrss    0                   
ru_idrss     0                   
ru_isrss     0                   
ru_minflt    13352               
ru_majflt    0                   
ru_nswap     0                   
ru_inblock   0                   
ru_oublock   0                   
ru_msgsnd    0                   
ru_msgrcv    0                   
ru_nsignals  0                   
ru_nvcsw     117                 
ru_nivcsw    30                  
cpu          0.140        
mem          0.000             
io           0.000             
iow          0.000             
maxvmem      0.000
arid         undefined

    OR
    
error: job id 1306546 not found

    """
    # match line of form  "   12 0.00000 job-101    yabi         qw    10/13/2009 10:42:52                                    1        "
    regexp = re.compile(r"^(\S+)\s+(.+)$")
    
    def __init__(self):
        self.err = ""
        self.out = ""
        self.exitcode = None
        
        # where we store the data gathered from the process
        self.info = {}
        
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
                key,val = re_match.groups()
                self.info[key] = val
                if DEBUG:
                    print key,"=>",val
                #print "id",jobid
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        
    def isDone(self):
        return self.exitcode != None
    
def qacct_spawn(jobid):
    """return the status of a running job via qstat
    /opt/sge/6.2u3/bin/lx24-amd64/qstat -u yabi
    """
    subenv = os.environ.copy()
    pp = QstatProcessProtocol()
    
    if DEBUG:
        print [
                                QACCT_COMMAND,
                                "-j",
                                jobid
                            ]
    
    reactor.spawnProcess(   pp,
                            QACCT_COMMAND, 
                            args=[
                                QACCT_COMMAND,
                                "-j",
                                jobid
                            ],
                            env=subenv
                        )

    return pp



from ex.connector.ExecConnector import ExecutionError
def qstat(user="yabi"):
    # run the qsub process.
    pp = qstat_spawn(user)
    
    while not pp.isDone():
        stackless.schedule()
        
    if pp.exitcode!=0:
        err = pp.err
        raise ExecutionError(err)

    # now we annotate our jobs with qstat -u username -f -j jobnum
    for jobnum in pp.jobs.keys():
        pp = qstat_verbose_spawn(pp.jobs,user,jobnum)

        while not pp.isDone():
            stackless.schedule()

        if pp.exitcode!=0:
            err = pp.err
            raise ExecutionError(err)

    return pp.jobs
    
def qacct(jobid):
    # run qacct
    pp = qacct_spawn(jobid)
    
    while not pp.isDone():
        stackless.schedule()
        
    if pp.exitcode!=0:
        err = pp.err
        raise ExecutionError(err) 
    
    return pp.info


