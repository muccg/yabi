# Create your views here.

from yabi.UploadStreamer import UploadStreamer
from yabiengine.backendhelper import make_hmac
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from urlparse import urlparse
from urllib import quote
import json
from django.conf import settings

from yaphc import Http, PostRequest, UnauthorizedError
from yabiadmin.yabiengine.backendhelper import BackendRefusedConnection, BackendHostUnreachable, PermissionDenied, FileNotFound, BackendStatusCodeError
from yabiadmin.yabiengine.backendhelper import get_fs_backendcredential_for_uri

import logging
logger = logging.getLogger(__name__)

DEBUG_UPLOAD_STREAMER = True

#
# Our upload streamer
#
class FileUploadStreamer(UploadStreamer):
    def __init__(self, host, port, selector, cookies, fields):
        UploadStreamer.__init__(self)
        self._host = host
        self._port = port
        self._selector = selector
        self._fields = fields
        self._cookies = cookies
    
    def receive_data_chunk(self, raw_data, start):
        if DEBUG_UPLOAD_STREAMER:
            print "STREAMER: receive_data_chunk", len(raw_data), start
        return self.file_data(raw_data)
    
    def file_complete(self, file_size):
        """individual file upload complete"""
        if DEBUG_UPLOAD_STREAMER:
            print "STREAMER: file_complete",file_size
        logger.info("Streaming through of file %s has been completed. %d bytes have been transferred." % (self._present_file, file_size))
        return self.end_file()
    
    def new_file(self, field_name, file_name, content_type, content_length, charset):
        """beginning of new file in upload"""
        if DEBUG_UPLOAD_STREAMER:
            print "STREAMER: new_file",field_name, file_name, content_type, content_length, charset
        return UploadStreamer.new_file(self,file_name)
    
    def upload_complete(self):
        """all files completely uploaded"""
        if DEBUG_UPLOAD_STREAMER:
            print "STREAMER: upload_complete"
        return self.end_connection()
    
    def handle_raw_input(self, input_data, META, content_length, boundary, encoding):
        """raw input"""
        if DEBUG_UPLOAD_STREAMER:
            print "STREAMER: handle_raw_input"
        # this is called right at the beginning. So we grab the uri detail here and initialise the outgoing POST
        self.post_multipart(host=self._host, port=self._port, selector=self._selector, cookies=self._cookies )

#@authentication_required
def put(request, yabiusername):
    """
    Uploads a file to the supplied URI
    """
    import socket
    import httplib

    try:
        logger.debug("uri: %s" %(request.GET['uri']))
        uri = request.GET['uri']

        bc = get_fs_backendcredential_for_uri(yabiusername, uri)
        decrypt_cred = bc.credential.get()
        resource = "%s?uri=%s" % (settings.YABIBACKEND_PUT, quote(uri))

        # TODO: the following is using GET parameters to push the decrypt creds onto the backend. This will probably make them show up in the backend logs
        # we should push them via POST parameters, or at least not log them in the backend.
        resource += "&username=%s&password=%s&cert=%s&key=%s"%(quote(decrypt_cred['username']),quote(decrypt_cred['password']),quote( decrypt_cred['cert']),quote(decrypt_cred['key']))

        streamer = FileUploadStreamer(host=settings.BACKEND_IP, port=settings.BACKEND_PORT or 80, selector=resource, cookies=[], fields=[])
        request.upload_handlers = [ streamer ]

        # evaluating POST triggers the processing of the request body
        request.POST
        
        result=streamer.stream.getresponse()
        
        content=result.read()
        status=int(result.status)
        reason = result.reason
        
        #print "passing back",status,reason,"in json snippet"
        
        response = {
            "level":"success" if status==200 else "failure",
            "message":content
            }
        return HttpResponse(content=json.dumps(response))

    except BackendRefusedConnection, e:
        return JsonMessageResponseNotFound(BACKEND_REFUSED_CONNECTION_MESSAGE)
    except socket.error, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e))
        raise
    except httplib.CannotSendRequest, e:
        logger.critical("Error connecting to %s: %s" % (settings.YABIBACKEND_SERVER, e.message))
        raise
    except UnauthorizedError, e:
        logger.critical("Unauthorized Error connecting to %s: %s. Is the HMAC set correctly?" % (settings.YABIBACKEND_SERVER, e.message))
        raise

