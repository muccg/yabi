# -*- coding: utf-8 -*-
from ExecConnector import ExecConnector, ExecutionError

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['SGE_ROOT','PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = ['SGE_ROOT']

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "sge"

DEBUG = False

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

class SGEConnector(ExecConnector):
    def __init__(self):
        print "SGEConnector::__init__() debug setting is",DEBUG
        ExecConnector.__init__(self)
    
    def run(self, yabiusername, command, working, scheme, username, host, channel, stdout="STDOUT.txt", stderr="STDERR.txt", maxWallTime=60, maxMemory=1024, cpus=1, queue="testing", jobType="single", module=None, **creds):
        try:
            if DEBUG:
                print "QSUB",command,"WORKING:",working
            jobid = qsub("jobname", command=command, user=username, workingdir=working, modules = [] if not module else [X.strip() for X in module.split(",")])
            if DEBUG:
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
            
            jobsummary = qstat(user=username)
            
            if jobid in jobsummary:
                # job has not finished
                status = jobsummary[jobid]['status']
                newstate = dict(qw="Unsubmitted", t="Pending",r="Running",hqw="Unsubmitted",ht="Pending",h="Pending",E="Error",Eqw="Error")[status]
            else:
                # job has finished
                sleep(15.0)                      # deal with SGE flush bizarreness (files dont flush from remote host immediately. Totally retarded)
                newstate = "Done"
            if DEBUG:
                print "Job summary:",jobsummary
                
            
            if state!=newstate:
                state=newstate
                client_stream.write("%s\n"%state)
                
            if state=="Error":
                client_stream.finish()
                return
            
            
        client_stream.finish()
     