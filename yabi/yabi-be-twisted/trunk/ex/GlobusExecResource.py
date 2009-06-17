
from twisted.web2 import resource, http_headers, responsecode, http, server, stream
from twisted.internet import defer, reactor
from os.path import sep
import os, json, sys
from submit_helpers import parsePOSTData, parsePUTData, parsePOSTDataRemoteWriter
from twisted.web2.auth.interfaces import IAuthenticatedRequest, IHTTPUser
from twisted.python.failure import Failure
import globus

from twisted.web import client
import json

import subprocess

from BaseExecResource import BaseExecResource

class GlobusExecResource(BaseExecResource):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    addSlash = False
    
    # self.XXXXX parameters we are allowed to override via POST parameters. These strings are followed by their type to cast to
    ALLOWED_OVERRIDE = [("maxWallTime",int), ("maxMemory",int), ("cpus",int), ("queue",str), ("jobType",str)]
    
    def __init__(self,request=None,path=None,address='https://xe-ng2.ivec.org:8443/wsrf/services/ManagedJobFactoryService', maxWallTime=60, maxMemory=1024, cpus=1, queue="normal", jobType="single", backend=None, authproxy=None, jobs=None):
        """Pass in the backends to be served out by this FSResource"""
        
        BaseExecResource.__init__(self,request,path)
        
        # save the details of this connector
        self.address, self.maxWallTime, self.maxMemory, self.cpus, self.queue, self.jobType = address, maxWallTime, maxMemory, cpus, queue, jobType
        
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
            self.jobs = globus.Jobs.Jobs(self.authproxy)
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
        
        # callback for when input data processing is completed
        def callback(result):
            print "cb1"
            args = request.args
            
            if "command" not in args:
                return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "Job submission must have a command!")
            
            for key, cast in self.ALLOWED_OVERRIDE:
                if key in args:
                    try:
                        val = cast(args[key][0])
                    except ValueError, ve:
                        return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "Cannot convert parameter '%s' to %s\n"%(key,cast))
                    print "setting",key,"to",cast(args[key][0])
                    setattr(self,key,cast(args[key][0]))
                    
            rsl = globus.ConstructRSL(
                command = args['command'][0],
                address = self.address,
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
            
            # when we have authed... do this
            def auth_success(deferred):
                # we should spawn our process to submit the job
                usercert = self.authproxy.ProxyFile(self.username)
                proc = globus.Run.run(usercert,rslfile)
                print "spawned",proc
                
                # now we watch this processes stdout stream... we _should_ get...
                ### Submitting job...Done.
                ### Job ID: uuid:aba9f032-5a25-11de-958c-000d6014d65a
                ### Termination time: 06/17/2009 03:27 GMT
                # then a pause
                # then something like...
                ### Current job state: Pending
                ### Current job state: Done
                ### Destroying job...Done.
                
                # TODO: use a deferred that waits on the stdout stream, rather than a timed callback
                from twisted.web2.stream import readStream
                
                def _got_data(data):
                    print "_g_d1 ->",data,"<-"
                    if data:
                        print "DATA",data,"END"
                        
                        # job submission has a result.
                        line = [l.strip() for l in data.split("\n")]
                        
                        # line 0... submit status
                        assert line[0].startswith("Submitting job...")
                        submit_status = line[0].split(".",3)[-1]
                        print "Submit status:",submit_status
                        
                        if submit_status!='Done.':
                            raise Exception, "Submission failed! %s"%submit_status
                        
                        # line 1... job id
                        assert line[1].startswith("Job ID:")
                        job_id = line[1].split(":")[-1]
                        print "Job ID:", job_id
                        
                        # line 2... termination time
                        assert line[2].startswith("Termination time:")
                        term_time = line[2].split(":",1)[-1]
                        
                        # line 3... EPR XML
                        epr_xml = line[3]
                        assert "EndpointReferenceType" in epr_xml
                        
                        # OK. job submission is done... So we can return the 200 OK response code. We use a stream to keep pumping the data down, then we close the stream when done.
                        client_stream = stream.ProducerStream()
                        client_channel.callback( http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))
                        
                        def callback(uuid,state):
                            print "uuid:",uuid,"state:",state
                            client_stream.write("%s\n"%state)
                            
                            if state=="Done":
                                client_stream.finish()
                            
                        def errback(uuid,error):
                            error = "Job status check failed!: %s - %s\n"%(uuid,error)
                            client_stream.write(error)
                            print error
                            client_stream.finish()                      # close it. we're cactus
                        
                        self.jobs.AddJob( job_id, self.username, epr_xml, callback=callback, errback=errback )
                        
                        # finish up this stream
                        raise Exception, "close stream"
                        
                # this deferred will be triggered on finish
                print "STDOUT=",proc.stdout
                print dir(proc.stdout)
                deferred = readStream(proc.stdout, _got_data)
                
                # when we are finished, trigger the cliennt channel to respond
                deferred.addCallback( lambda res: client_channel.callback( http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Stream finished: %s\n"%(res)) ) )
                
                def stream_errorback(fail):
                    if isinstance(fail,Failure):
                        if fail.getErrorMessage()=="close stream":
                            fail.trap(Exception)
                            print "Stream closed"
                            return None
                        else:
                            return fail
                    else:
                        client_channel.callback( http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "Job stream failed!: %s\n"%(fail)) )
                    return Failure(fail)
                    
                deferred.addErrback( stream_errorback )
                
            
            # first we need to auth, if not authed already
            if not self.authproxy.IsProxyValid(self.username):
                # we have to auth the user. we need to get the credentials json object from the admin mango app
                self.AuthProxyUser(self.username,self.backend, auth_success,client_channel)
            else:
                # auth our user
                auth_success(deferred)
        
            return client_channel
            
            #return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Job Submission OK %s\n"%result)
            
        deferred.addCallback(callback)
        deferred.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "Job Submission Failed %s\n"%res) )
        
        return deferred

     
    def AuthProxyUser(self, username, backend, successcallback, deferred, *args):
        """Auth a user via getting the credentials from the json yabiadmin backend. When the credentials are gathered, successcallback is called with the deferred.
        The deferred should be the result channel your result will go back down"""
        host,port = "localhost",8000
        useragent = "YabiFS/0.1"
        
        factory = client.HTTPClientFactory(
            'http://%s:%d/yabiadmin/ws/credential/%s/%s/'%(host,port,username,backend),
            agent = useragent
            )
        reactor.connectTCP(host, port, factory)
        
        # now if the page fails for some reason. deal with it
        def _doFailure(data):
            print "Failed:",factory,":",type(data),data.__class__
            print data
            
            deferred.callback( http.Response( responsecode.UNAUTHORIZED, {'content-type': http_headers.MimeType('text', 'plain')}, "User: %s does not have credentials for this backend\n"%username) )
            
        # if we get the credentials decode them and auth them
        def _doSuccess(data):
            print "Success",deferred,args,successcallback
            credentials=json.loads(data)
            print "Credentials gathered successfully for user %s"%username
            
            # auth the user
            self.authproxy.CreateUserProxy(username,credentials['cert'],credentials['key'],credentials['password'])
            
            successcallback(deferred, *args)
        
        return factory.deferred.addCallback(_doSuccess).addErrback(_doFailure)

    def locateChild(self, request, segments):
        # return our local file resource for these segments
        #print "LFR::LC",request,segments
        return GlobusExecResource(request,segments,address=self.address,maxWallTime=self.maxWallTime,maxMemory=self.maxMemory,cpus=self.cpus,queue=self.queue,jobType=self.jobType, backend=self.backend, authproxy=self.authproxy, jobs=self.jobs), []
    