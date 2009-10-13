from ExecConnector import ExecConnector, ExecutionError
from twisted.web2 import http, responsecode, http_headers

import shlex
import globus
import stackless
import tempfile

from utils.stacklesstools import sleep
from utils.sgetools import qsub, qstat
# for Job status updates, poll this often
def JobPollGeneratorDefault():
    """Generator for these MUST be infinite. Cause you don't know how long the job will take. Default is to hit it pretty hard."""
    delay = 1.0
    while delay<10.0:
        yield delay
        delay *= 1.05           # increase by 5%
    
    while True:
        yield 10.0

class SGEConnector(ExecConnector, globus.Auth):
    def __init__(self):
        self.CreateAuthProxy()
    
    def run(self, command, working, scheme, username, host, channel, stdout="STDOUT.txt", stderr="STDERR.txt", maxWallTime=60, maxMemory=1024, cpus=1, queue="testing", jobType="single"):
        try:
            res = qsub("jobname", username, command)
        
            print "RESULT",res
        
        except ExecutionError, ee:
            channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream = str(ee) ))
        
    def oldrun(self, command, working, scheme, username, host, channel, stdout="STDOUT.txt", stderr="STDERR.txt", maxWallTime=60, maxMemory=1024, cpus=1, queue="testing", jobType="single"):
        # save the epr to a tempfile so we can use it again and again
        temp = tempfile.NamedTemporaryFile(suffix=".epr",delete=False)
        temp.write(epr)
        temp.close()
            
        eprfile = temp.name
            
        state = None
        delay = JobPollGeneratorDefault()
        while state!="Done":
            # pause
            sleep(delay.next())
            
            self.EnsureAuthed(scheme,username,host)
            processprotocol = globus.Run.status( usercert, eprfile, host )
            
            while not processprotocol.isDone():
                stackless.schedule()
                
            #print "STATE:",processprotocol.jobstate, processprotocol.exitcode
                
            if processprotocol.exitcode and processprotocol.jobstate!="Done":
                # error occured running statecheck... sometimes globus just fails cause its a fucktard.
                print "Job status check for %s Failed (%d) - %s / %s\n"%(job_id,processprotocol.exitcode,processprotocol.out,processprotocol.err)
                channel.write("Failed - %s\n"%(processprotocol.err))
                channel.finish()
                return
            
            newstate = processprotocol.jobstate
            if state!=newstate:
                state=newstate
                channel.write("%s\n"%state)
            
            
        channel.finish()
       