from ExecConnector import ExecConnector, ExecutionError
from twisted.web2 import http, responsecode, http_headers, stream

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
            jobid = qsub("jobname", command=command, user=username)
            print "JOB ID",jobid
        
        except ExecutionError, ee:
            channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream = str(ee) ))
            return
        
        # send an OK message, but leave the stream open
        client_stream = stream.ProducerStream()
        channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))
        
        state = None
        delay = JobPollGeneratorDefault()
        while state!="Done":
            # pause
            sleep(delay.next())
            
            jobsummary = qstat()
            
            if jobid in jobsummary:
                # job has not finished
                status = jobsummary[jobid]['status']
                newstate = dict(qw="Unsubmitted", t="Pending",r="Running",hqw="Unsubmitted",ht="Pending",h="Pending",E="Error")[status]
            else:
                # job has finished
                newstate = "Done"
            print "Job summary:",jobsummary
                
            
            if state!=newstate:
                state=newstate
                client_stream.write("%s\n"%state)
            
            
        client_stream.finish()
     