# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
# -*- coding: utf-8 -*-
from twistedweb2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor
import weakref, json
import sys, os, signal
import gevent
import traceback
from Exceptions import BlockingException

# how often to check back on a process. 
PROCESS_CHECK_TIME = 0.01

from utils.parsers import parse_url

from utils.submit_helpers import parsePOSTData

from decorators import hmac_authenticated

DEFAULT_COPY_PRIORITY = 1                   # not immediate by default but high priority

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
        

    @hmac_authenticated
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

    @hmac_authenticated
    def handle_copy(self, request):
        # override default priority
        priority = int(request.args['priority'][0]) if "priority" in request.args else DEFAULT_COPY_PRIORITY

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
        src_port = src_address.port
        dst_port = dst_address.port
        
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
        #if sbend == dbend:
            #locks = [sbend.lock(),None]
        #else:
            #locks = [sbend.lock(),dbend.lock()]
        
        if DEBUG:
            print "src_hostname",src_hostname
            print "src_username",src_username
            print "src_path",src_path, src_filename
            print "dst_hostname",dst_hostname
            print "dst_username",dst_username
            print "dst_path",dst_path, dst_filename
            print "creds:",creds
        
        # if no dest filename is provided, use the src_filename
        dst_filename = src_filename if not len(dst_filename) else dst_filename
        
        def copy(channel):
            try:
                writeproto, fifo = dbend.GetWriteFifo(dst_hostname, dst_username, dst_path, dst_port, dst_filename,yabiusername=yabiusername,creds=creds['dst'] if 'dst' in creds else {})
                readproto, fifo2 = sbend.GetReadFifo(src_hostname, src_username, src_path, src_port, src_filename, fifo,yabiusername=yabiusername,creds=creds['src'] if 'src' in creds else {})
                
                def fifo_cleanup(response):
                    os.unlink(fifo)
                    return response
                channel.addCallback(fifo_cleanup)
                
            except BlockingException, be:
                #sbend.unlock(locks[0])
                #if locks[1]:
                    #dbend.unlock(locks[1])
                print traceback.format_exc()
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
                gevent.sleep()
            
            # if one died and not the other, then kill the non dead one
            if readproto.isDone() and readproto.exitcode!=0 and not writeproto.isDone():
                # readproto failed. write proto is still running. Kill it
                if DEBUG:
                    print "READ FAILED",readproto.exitcode,writeproto.exitcode
                print "read failed. attempting os.kill(",writeproto.transport.pid,",",signal.SIGKILL,")",type(writeproto.transport.pid),type(signal.SIGKILL)
                while writeproto.transport.pid==None:
                    #print "writeproto transport pid not set. waiting for setting..."
                    gevent.sleep()
                os.kill(writeproto.transport.pid, signal.SIGKILL)
            else:
                # wait for write to finish
                if DEBUG:
                    print "WFW",readproto.exitcode,writeproto.exitcode
                while writeproto.exitcode == None:
                    gevent.sleep()
                
                # did write succeed?
                if writeproto.exitcode == 0:
                    if DEBUG:
                        print "WFR",readproto.exitcode,writeproto.exitcode
                    while readproto.exitcode == None:
                        gevent.sleep()
            
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
                
            #sbend.unlock(locks[0])
            #if locks[1]:
                #dbend.unlock(locks[1])
            
        client_channel = defer.Deferred()
        
        tasklet = gevent.spawn(copy,client_channel)
        
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
        deferred.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "Copy Submission Failed %s\n"%res) )
        
        return deferred

    def http_GET(self, request):
        return self.handle_copy(request)

