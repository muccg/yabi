
from twisted.web2 import resource, http_headers, responsecode, http, server, stream
from twisted.internet import defer, reactor
from os.path import sep
import os, json, sys
from submit_helpers import parsePOSTData, parsePUTData, parsePOSTDataRemoteWriter
from twisted.web2.auth.interfaces import IAuthenticatedRequest, IHTTPUser
from twisted.python.failure import Failure
import globus

from twisted.web import client
import json, shlex

import subprocess
import stackless
import tempfile

from utils.stacklesstools import GET, GETFailure, sleep

from BaseExecResource import BaseExecResource

# for Job status updates, poll this often
def JobPollGeneratorDefault():
    """Generator for these MUST be infinite. Cause you don't know how long the job will take. Default is to hit it pretty hard."""
    delay = 1.0
    while delay<10.0:
        yield delay
        delay *= 1.05           # increase by 5%
    
    while True:
        yield 10.0

class GlobusExecResource(BaseExecResource, globus.Auth):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    addSlash = False
    
    # self.XXXXX parameters we are allowed to override via POST parameters. These strings are followed by their type to cast to
    ALLOWED_OVERRIDE = [("maxWallTime",int), ("maxMemory",int), ("cpus",int), ("queue",str), ("jobType",str), ("directory",str), ("stdout",str), ("stderr",str)]
    
    def __init__(self,request=None,path=None,host='xe-gt4.ivec.org', maxWallTime=60, maxMemory=1024, cpus=1, queue="normal", jobType="single", stdout="/dev/null", stderr="/dev/null", directory="/scratch/bi01/cwellington", dirprefix="/scratch", backend=None, authproxy=None, jobs=None):
        """dirprefix is to be used to make the exec scratch dir and dir paths have the same "hidden root" as the filesystem backends. if
        we have /scratch mounted on a fs backend as /fs/gridftp1/, then we cant have working directories set with "/scratch/bi01/cwellington", 
        the prefix should be implied!
        """
        BaseExecResource.__init__(self,request,path)
        
        # save the details of this connector
        self.host, self.maxWallTime, self.maxMemory, self.cpus,self.queue, self.jobType, self.stdout, self.stderr, self.directory, self.dirprefix = \
             host,      maxWallTime,      maxMemory,      cpus,     queue,      jobType,      stdout,      stderr,      directory,      dirprefix
         
        # our backend identifier (for mango)
        self.backend = backend
        
        if path:
            assert len(path)==1, "More than just username passed in as the path"
            
            # first part of path is yabi_username
            self.username = path[0]
            
            # together the whole thing is the path
            self.path=path
        else:
            self.path = None
            
        if not authproxy:
            self.authproxy = globus.CertificateProxy()
        else:
            self.authproxy = authproxy
            
        if not jobs:
            self.jobs = globus.Jobs.Jobs(self.authproxy,self.backend)
        else:
            self.jobs = jobs
            
            
    def http_POST(self, request):
        """
        Respond to a POST request.
        Reads and parses the incoming body data then calls L{render}.
    
        @param request: the request to process.
        @return: an object adaptable to L{iweb.IResponse}.
        """
        if self.path == None:
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Globus Exec Connector Version: %s\n"%self.VERSION)
        
        deferred = parsePOSTDataRemoteWriter(request)
        
        def post_parsed(result):
            args = request.args
            
            if "command" not in args:
                return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "Job submission must have a command!")
            
            # cast any allowed override variables into their proper format
            for key, cast in self.ALLOWED_OVERRIDE:
                if key in args:
                    try:
                        val = cast(args[key][0])
                    except ValueError, ve:
                        return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "Cannot convert parameter '%s' to %s\n"%(key,cast))
                    #print "setting",key,"to",cast(args[key][0])
                    setattr(self,key,cast(args[key][0]))
            
            # use shlex to parse the command into executable and arguments
            command_string = args['command'][0]
            lexer = shlex.shlex(command_string, posix=True)
            lexer.wordchars += r"-.:;/"
            arguments = list(lexer)
            
            rsl = globus.ConstructRSL(
                command = arguments[0],
                args = arguments[1:],
                directory = self.directory,
                stdout = self.stdout,
                stderr = self.stderr,
                address = self.host,
                maxWallTime = self.maxWallTime,
                maxMemory = self.maxMemory,
                cpus = self.cpus,
                queue = self.queue,
                jobType = self.jobType
            )
            
            # store the rsl in a file
            rslfile = globus.writersltofile(rsl)
            
            # we are gonna try submitting the job. We will need to make a deferred to return, because this could take a while
            client_channel = defer.Deferred()
            
            # now before we return we want to make a stackless tasklet to handle the job submission
            def submit_job(channel):
                """Submit a job to the globus backend. 'channel' is the channel we will send our final result to the client down"""
                # first we need to auth the proxy
                self.EnsureAuthed()
                
                # we return "200 OK" now, but keep the stream open for status updates
                client_stream = stream.ProducerStream()
                channel.callback( http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))
                
                # now submit the job via globus
                usercert = self.authproxy.ProxyFile(self.username)
                
                # TODO: what if our proxy has expired in the meantime? (rare, but possible)
                processprotocol = globus.Run.run( usercert, rslfile, self.host)
                
                while not processprotocol.isDone():
                    stackless.schedule()
                    
                assert processprotocol.exitcode==0
                
                # now we want to continually check the status of the job
                job_id = processprotocol.job_id
                epr = processprotocol.epr
                
                # save the epr to a tempfile so we can use it again and again
                temp = tempfile.NamedTemporaryFile(suffix=".epr",delete=False)
                temp.write(epr)
                temp.close()
                 
                eprfile = temp.name
                 
                state = None
                delay = JobPollGeneratorDefault()
                while state!="Done":
                    self.EnsureAuthed()
                    processprotocol = globus.Run.status( usercert, eprfile, self.host )
                    
                    while not processprotocol.isDone():
                        stackless.schedule()
                        
                    if processprotocol.exitcode:
                        # error occured running statecheck... sometimes globus just fails cause its a fucktard.
                        print "Job status check for %s Failed - %s\n"%(job_id,processprotocol.err)
                        client_stream.write("Failed - %s\n"%(processprotocol.err))
                        client_stream.finish()
                        return
                    
                    state = processprotocol.jobstate
                    client_stream.write("%s\n"%state)
                    
                    # pause
                    sleep(delay.next())
                    
                    
                client_stream.finish()
            
            task = stackless.tasklet(submit_job)
            task.setup(client_channel)
            task.run()
            
            return client_channel
        
        deferred.addCallback(post_parsed)
        deferred.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "Job Submission Failed %s\n"%res) )
        
        return deferred

    def locateChild(self, request, segments):
        # return our local file resource for these segments
        #print "LFR::LC",request,segments
        return GlobusExecResource(
                request,
                segments,
                host=self.host,
                maxWallTime=self.maxWallTime,
                maxMemory=self.maxMemory,
                cpus=self.cpus,
                queue=self.queue,
                jobType=self.jobType,
                stdout=self.stdout,
                stderr=self.stderr,
                directory=self.directory,
                dirprefix=self.dirprefix,
                backend=self.backend,
                authproxy=self.authproxy,
                jobs=self.jobs
            ), []
    
