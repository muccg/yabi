# -*- coding: utf-8 -*-
from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor
import weakref, json
import sys, os, signal
import stackless
from Exceptions import BlockingException

# how often to check back on a process. 
PROCESS_CHECK_TIME = 0.01

from utils.parsers import parse_url

from utils.submit_helpers import parsePOSTData

DEBUG = False

# module level storage for a summary of all the present copy jobs
# key = yabiusername
# value = (src,dst,readprocproto_weakref, writeprocproto_weakref)
copies_in_progress = {}

class FileCopyProgressResource(resource.Resource):
    @staticmethod
    def _users_details(username):
        stale_entries = []
        response=[]
        for src,dst,read,write in copies_in_progress[username]:
            if read()==None and write()==None:
                stale_entries.append((src,dst,read,write))
            else:
                response.append({"src":src, "dst":dst})
                
        # purge stale entries for this user if there are any
        for tup in stale_entries:
            copies_in_progress[key].remove(tup)
        
        return response
        
    
    def http_GET(self, request):
        if 'yabiusername' in request.args:
            yabiusername = request.args['yabiusername'][0]
            if yabiusername not in copies_in_progress:
                # requested user has no copies or user is bogus. Either way return nothing
                return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'json')}, json.dumps([])+"\n" )
            else:
                return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'json')}, json.dumps(self._users_details(yabiusername))+"\n" )
         
        users = copies_in_progress.keys()
        response = {}
        keys_to_delete = []
        for user in users:
            response[str(user)] = self._users_details(user)
            
            if not len(copies_in_progress[user]):
                keys_to_delete.append(user)
            
        # purge stale keys
        for key in keys_to_delete:
            del copies_in_progress[key]
        
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'json')}, json.dumps(response)+"\n" )


class FileCopyResource(resource.PostableResource):
    VERSION=0.1
    maxMem = 100*1024
    maxFields = 16
    maxSize = 10*1024*102
    
    def __init__(self,request=None, path=None, fsresource=None):
        """Pass in the backends to be served out by this FSResource"""
        self.path = path
        
        if not fsresource:
            raise Exception, "FileCopyResource must be informed on construction as to which FSResource is its parent"
        
        self.fsresource = weakref.ref(fsresource)
        
    def handle_copy(self, request):
        # break our request path into parts
        #print "Copy",request,request.args
        if 'src' not in request.args or 'dst' not in request.args:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "copy must specify source 'src' and destination 'dst'\n")
        
        # compile any credentials together to pass to backend
        creds={}
        for part in ['src','dst']:
            for varname in ['key','password','username','cert']:
                keyname = "%s_%s"%(part,varname)
                if keyname in request.args:
                    if part not in creds:
                        creds[part]={}
                    creds[part][varname] = request.args[keyname][0]
                    del request.args[keyname]
        
        yabiusername = request.args['yabiusername'][0] if "yabiusername" in request.args else None
        
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        src = request.args['src'][0]
        dst = request.args['dst'][0]
            
        #print "Copying from %s -> %s"%(src,dst)
        
        src_scheme, src_address = parse_url(src)
        dst_scheme, dst_address = parse_url(dst)
        
        src_username = src_address.username
        dst_username = dst_address.username
        src_path, src_filename = os.path.split(src_address.path)
        dst_path, dst_filename = os.path.split(dst_address.path)
        src_hostname = src_address.hostname
        dst_hostname = dst_address.hostname
        
        # backends
        sbend = self.fsresource().GetBackend(src_scheme)
        dbend = self.fsresource().GetBackend(dst_scheme)
        
        # copying from
        #print "Copying from",sbend,"to",dbend
        
        # create our delay generator in case things go pear shape
        # TODO: actually use these things
        src_fail_delays = sbend.NonFatalRetryGenerator()
        dst_fail_delays = dbend.NonFatalRetryGenerator()
        
        src_retry_kws = sbend.NonFatalKeywords
        dst_retry_kws = dbend.NonFatalKeywords
        
        # if source and destination are the same, only make one lock on this backend
        if sbend == dbend:
            locks = [sbend.lock(),None]
        else:
            locks = [sbend.lock(),dbend.lock()]
        
        #print "src_hostname",src_hostname
        #print "src_username",src_username
        #print "src_path",src_path, src_filename
        #print "dst_hostname",dst_hostname
        #print "dst_username",dst_username
        #print "dst_path",dst_path, dst_filename
        
        # if no dest filename is provided, use the src_filename
        dst_filename = src_filename if not len(dst_filename) else dst_filename
        
        def copy(channel):
            try:
                writeproto, fifo = dbend.GetWriteFifo(dst_hostname, dst_username, dst_path, dst_filename,yabiusername=yabiusername,creds=creds['dst'] if 'dst' in creds else {})
                readproto, fifo2 = sbend.GetReadFifo(src_hostname, src_username, src_path, src_filename, fifo,yabiusername=yabiusername,creds=creds['src'] if 'src' in creds else {})
            except BlockingException, be:
                sbend.unlock(locks[0])
                if locks[1]:
                    dbend.unlock(locks[1])
                channel.callback(http.Response( responsecode.SERVICE_UNAVAILABLE, {'content-type': http_headers.MimeType('text', 'plain')}, str(be)))
                return
            
            # keep a weakref in the module level info store so we can get a profile of all copy operations
            if yabiusername not in copies_in_progress:
                copies_in_progress[yabiusername]=[]
            copies_in_progress[yabiusername].append( (src,dst,weakref.ref(readproto),weakref.ref(writeproto)) )
            
            if DEBUG:
                print "READ:",readproto,fifo2
                print "WRITE:",writeproto,fifo
                       
            # wait for one to finish
            while not readproto.isDone() and not writeproto.isDone():
                stackless.schedule()
            
            # if one died and not the other, then kill the non dead one
            if readproto.isDone() and readproto.exitcode!=0 and not writeproto.isDone():
                # readproto failed. write proto is still running. Kill it
                if DEBUG:
                    print "READ FAILED",readproto.exitcode,writeproto.exitcode
                print "read failed. attempting os.kill(",writeproto.transport.pid,",",signal.SIGKILL,")",type(writeproto.transport.pid),type(signal.SIGKILL)
                while writeproto.transport.pid==None:
                    print "writeproto transport pid not set. waiting for setting..."
                    stackless.schedule()
                os.kill(writeproto.transport.pid, signal.SIGKILL)
            else:
                # wait for write to finish
                if DEBUG:
                    print "WFW",readproto.exitcode,writeproto.exitcode
                while writeproto.exitcode == None:
                    stackless.schedule()
                
                # did write succeed?
                if writeproto.exitcode == 0:
                    if DEBUG:
                        print "WFR",readproto.exitcode,writeproto.exitcode
                    while readproto.exitcode == None:
                        stackless.schedule()
            
            if readproto.exitcode==0 and writeproto.exitcode==0:
                if DEBUG:
                    print "Copy finished exit codes 0"
                    print "readproto:"
                    print "ERR:",readproto.err
                    print "OUT:",readproto.out
                    print "writeproto:"
                    print "ERR:",writeproto.err
                    print "OUT:",writeproto.out
                    
                channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Copy OK\n"))
            else:
                rexit = "Killed" if readproto.exitcode==None else str(readproto.exitcode)
                wexit = "Killed" if writeproto.exitcode==None else str(writeproto.exitcode)
                
                msg = ("Copy failed:\n\nRead process: %s\n"+readproto.err+"\n\nWrite process: %s\n"+writeproto.err+"\n")%(rexit,wexit)
                #print "MSG",msg
                channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, msg))
                
            sbend.unlock(locks[0])
            if locks[1]:
                dbend.unlock(locks[1])
            
        client_channel = defer.Deferred()
        
        tasklet = stackless.tasklet(copy)
        tasklet.setup(client_channel)
        tasklet.run()
            
        return client_channel
            
    def http_POST(self, request):
        """
        Respond to a POST request.
        Reads and parses the incoming body data then calls L{render}.
    
        @param request: the request to process.
        @return: an object adaptable to L{iweb.IResponse}.
        """
        deferred = parsePOSTData(request)
        
        def post_parsed(result):
            return self.handle_copy(request)
        
        deferred.addCallback(post_parsed)
        deferred.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "Job Submission Failed %s\n"%res) )
        
        return deferred

    def http_GET(self, request):
        return self.handle_copy(request)

