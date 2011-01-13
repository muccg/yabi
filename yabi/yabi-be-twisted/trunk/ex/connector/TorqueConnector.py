# -*- coding: utf-8 -*-
from ExecConnector import ExecConnector, ExecutionError

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "torque"

DEBUG = False

from twisted.web2 import http, responsecode, http_headers, stream

from utils.stacklesstools import sleep, POST
from utils.torquetools import qsub, qstat

import json

from TaskManager.TaskTools import RemoteInfo

# for Job status updates, poll this often
def JobPollGeneratorDefault():
    """Generator for these MUST be infinite. Cause you don't know how long the job will take. Default is to hit it pretty hard."""
    delay = 1.0
    while delay<10.0:
        yield delay
        delay *= 1.05           # increase by 5%
    
    while True:
        yield 10.0

class TorqueConnector(ExecConnector):
    def __init__(self):
        print "TorqueConnector::__init__() debug setting is",DEBUG
        ExecConnector.__init__(self)
    
    def run(self, yabiusername, command, working, scheme, username, host, remote_url, channel, stdout="STDOUT.txt", stderr="STDERR.txt", maxWallTime=60, maxMemory=1024, cpus=1, queue="testing", jobType="single", module=None, **creds):
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
        
        # now the job is submitted, lets remember it
        self.add_running(jobid, {'username':username})
        
        # lets report our id to the caller
        client_stream.write("id=%s\n"%jobid)
        
        self.main_loop( client_stream, username, jobid, remote_url)
            
        # delete finished job
        self.del_running(jobid)
            
        client_stream.finish()

    def resume(self, jobid, yabiusername, command, working, scheme, username, host, channel, stdout="STDOUT.txt", stderr="STDERR.txt", walltime=60, max_memory=1024, cpus=1, queue="testing", job_type="single", module=None, **creds):
    #def resume(self,yabiusername, eprfile, scheme, username, host, **creds):
        # send an OK message, but leave the stream open
        client_stream = stream.ProducerStream()
        channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))

        username = self.get_running(jobid)['username']
        
        self.main_loop( client_stream, username, jobid )
        
        # delete finished job
        self.del_running(jobid)
            
        client_stream.finish()

    def main_loop(self, client_stream, username, jobid, remote_url=None ):
        newstate = state = None
        delay = JobPollGeneratorDefault()
        while state!="Done":
            # pause
            sleep(delay.next())
            
            print "calling qstat..."
            jobsummary = qstat(jobid, username)
            self.update_running(jobid,jobsummary)
            
            if jobid in jobsummary:
                # job has not finished
                status = jobsummary[jobid]['job_state']
                newstate = dict(Q="Unsubmitted", C="Done", E="Running", H="Pending", R="Running", T="Pending", W="Pending", S="Pending")[status]
            else:
                # job has finished
                sleep(15.0)                      # deal with SGE flush bizarreness (files dont flush from remote host immediately. Totally retarded)
                print "ERROR: jobid %s not in jobsummary"%jobid
                print "jobsummary is",jobsummary
                
                # if there is standard error from the qstat command, report that!
                
                
                newstate = "Error"
            if DEBUG:
                print "Job summary:",jobsummary
                
            
            if state!=newstate:
                state=newstate
                client_stream.write("%s\n"%state)
                
                # report the full status to the remote_url
                if remote_url:
                    if jobid in jobsummary:
                        RemoteInfo(remote_url,json.dumps(jobsummary[jobid]))
                    else:
                        print "Cannot call RemoteInfo call for job",jobid
                
            if state=="Error":
                client_stream.finish()
                return
        
    def info(self, jobid, username):
        jobsummary = qstat(user=username)
        print jobsummary
        
