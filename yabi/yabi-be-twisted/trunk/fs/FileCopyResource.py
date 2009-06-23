from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor
from submit_helpers import parsePOSTDataRemoteWriter
import weakref
import sys, os

# how often to check back on a process. 
PROCESS_CHECK_TIME = 0.01

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
        
    def render(self, request):
        # break our request path into parts
        return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "request must be POST\n")

    def http_POST(self, request):
        """
        Respond to a POST request.
        Reads and parses the incoming body data then calls L{render}.
    
        @param request: the request to process.
        @return: an object adaptable to L{iweb.IResponse}.
        
        NOTE: parameters must be Content-Type: application/x-www-form-urlencoded
        eg. 
        """
        print "POST!",request
        
        deferred = parsePOSTDataRemoteWriter( request,
            self.maxMem, self.maxFields, self.maxSize )
        
        # Copy command
        def CopyCommand(res):
            # source and destination
            if 'src' not in request.args or 'dst' not in request.args:
                return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "copy must specify source 'src' and destination 'dst'\n")
            
            src = request.args['src'][0]
            dst = request.args['dst'][0]
            
            print "Copying from %s -> %s"%(src,dst)
            
            # seperate out the backends
            src_be, src_path = src.split("/",1)
            dst_be, dst_path = dst.split("/",1)
            
            # get our actual backend objects
            sbend = getattr(self.fsresource(), "child_%s"%src_be)
            dbend = getattr(self.fsresource(), "child_%s"%dst_be)
            
            # if our destination path ends with a '/', append the filename from the source onto it. This makes sure we don't write out 
            # the destination file as "fifo_sdfsdf"
            if dst_path.endswith("/"):
                dst_path+=src_path.rsplit("/",1)[-1]
            
            print "Copying from",sbend,"to",dbend
            
            # create our delay generator in case things go pear shape
            src_fail_delays = sbend.NonFatalRetryGenerator()
            dst_fail_delays = dbend.NonFatalRetryGenerator()
            
            src_retry_kws = sbend.NonFatalKeywords
            dst_retry_kws = dbend.NonFatalKeywords
            
            # our http result channel. this stays open until the copy is finished
            result_channel = defer.Deferred()
            
            def _write_ready( procw, fifo ):
                #print "_write_ready(",procw,",",fifo,")"
                
                def _read_ready( procr, fifo ):
                    #print "_read_ready(",procr,",",fifo,")"
                    
                    # the connection should now be pumping. We now have to wait for both processes to terminate. Then we get these processes results
                    def check_processes(deferred, reader, writer):
                        #print "check_processes",reader,writer
                        
                        # we poll each process for exit codes.
                        wx = writer.poll()
                        rx = reader.poll()
                        
                        #print "wx:",wx,"rx:",rx
                        
                        ##
                        ## TODO: check this following logic thouroughly
                        ##
                        if (wx==None and rx==None) or (wx==None and rx==0) or (wx==0 and rx==None):
                            # recall ourselves later. both haven't finished
                            reactor.callLater(PROCESS_CHECK_TIME, check_processes, deferred, reader, writer)
                        else:
                            # we have one giving an exit code.
                            read_stdout=""
                            write_stdout=""
                            if rx:
                                read_stdout = reader.stdout.read()
                            if wx:
                                write_stdout = writer.stdout.read()
                            
                            if wx==0 and rx==0:
                                # success
                                print "File copy done!"
                                return deferred.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream="File copied successfuly!\n"))
                            else:
                                # something went wrong with one of the processes. If a process is still alive, kill it
                                if wx==None:
                                    #print "killing writer ",writer
                                    writer.kill()
                                    #wx = "Killed due to error on reader"
                                if rx==None:
                                    #print "killing reader ",reader
                                    reader.kill()
                                    #rx = "Killed due to error on writer"
                                    
                                
                                if True in ["Permission denied" in error for error in (read_stdout, write_stdout)]:
                                    return deferred.callback(http.Response( responsecode.NOT_ALLOWED, {'content-type': http_headers.MimeType('text', 'plain')}, stream="File copy failed! Permission denied\n"))
                                elif True in ["No such file or directory" in error for error in (read_stdout, write_stdout)]:
                                    return deferred.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream="File copy failed! No such file or directory\n"))
                                else:
                                    next_delay = 0.0
                                    
                                    # check for temporary failures. check each backend at a time
                                    for bendphrase, benderror, bendgen in [ (src_retry_kws, read_stdout, src_fail_delays), (dst_retry_kws, write_stdout, dst_fail_delays) ]:
                                        # is this backend temporarily failing
                                        #print "checking",bendphrase,",", benderror,",", bendgen
                                        #print "found?",[(phrase,error) for phrase in bendphrase for error in benderror]
                                        if True in [phrase.lower() in benderror.lower() for phrase in bendphrase]:
                                            #print "found!"
                                            # temporary error. lets get our next delay for this backend
                                            next_delay = bendgen.next()
                                    
                                    if next_delay:
                                        print "Temporary failure. delaying for %.1f seconds."%next_delay
                                        
                                        # retrigger the whole thing again in this many seconds
                                        reactor.callLater( next_delay, dbend.GetWriteFifo, dst_path, _write_ready)
                                        return
                                    else:
                                        response  = "Read process:\nexit code:%s\noutput:%s\n\n--------------------\n\n"%(rx,read_stdout)
                                        response += "Write process:\nexit code:%s\noutput:%s\n\n--------------------\n\n"%(wx,write_stdout)
                                        return deferred.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream="File copy failed!\n"+response))
                    
                    reactor.callLater(PROCESS_CHECK_TIME, check_processes, result_channel, procr, procw)
                
                sbend.GetReadFifo(src_path, _read_ready, fifo)
                
            dbend.GetWriteFifo(dst_path, _write_ready)
            
            return result_channel
            
            #return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "OK: %s\n"%res)
        
        deferred.addCallback(CopyCommand)
        
        # save failed
        deferred.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "NOT OK: %s\n"%str(res)) )
        
        return deferred
        
