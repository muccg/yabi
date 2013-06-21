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
import httplib
import random
import mimetypes
import hmac
from django.conf import settings
from django.core.files.uploadhandler import FileUploadHandler


class UploadStreamer(FileUploadHandler):
    BOUNDARY_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    CRLF = "\r\n"
    
    def __init__(self):
        FileUploadHandler.__init__(self)
        self._buff = ""
        self._present_file = None
        self._file_count = 0
        self.BOUNDARY = self.encode_multipart_make_boundary()
    
    def encode_multipart_make_boundary(self):
        boundary = "".join([random.choice(self.BOUNDARY_CHARS) for X in range(28)])
        return boundary

    def encode_multipart_content_type(self):
        return 'multipart/form-data; boundary="%s"' % self.BOUNDARY
    
    def get_content_type(self,filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
    def post_multipart(self, host, port, selector, cookies=None):
        """
        Post fields and files to an http host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return the server's response page.
        """
        content_type = self.encode_multipart_content_type()
        
        self.stream = httplib.HTTPConnection(host=host, port=port)
        self.stream.putrequest('POST', selector)
        self.stream.putheader('Content-Type', content_type)
        if cookies:
            for cookie in cookies:
                self.stream.putheader("Cookie",cookie)
        self.stream.putheader('Transfer-Encoding', 'chunked')
        self.stream.putheader('User-Agent', 'YabiUploadStreamer/0.0')
        self.stream.putheader('Expect','100-continue')
        self.stream.putheader('Accept','*/*')
        
        hmac_digest = hmac.new(settings.HMAC_KEY)
        hmac_digest.update(selector)
        self.stream.putheader("Hmac-digest", hmac_digest.hexdigest())
        
        self.stream.endheaders()
    
    def send(self, string):
        if type(string) is unicode:
            string = str(string)
        self._buff += string
            
    def flush(self):
        """flush the buffer"""
        self.stream.send(hex(len(self._buff))[2:].upper()+self.CRLF)
        self.stream.send(self._buff)
        self.stream.send(self.CRLF)
        self._buff = ""
    
    def send_fields(self,fields):
        for (key,value) in fields:
            self.send('--' + self.BOUNDARY + self.CRLF)
            self.send('Content-Disposition: form-data; name="%s"' % key + self.CRLF)
            self.send(self.CRLF)
            self.send(value)
            self.send(self.CRLF)
            
        self.flush()
        
    def new_file(self, filename):
        assert self._present_file == None
        self._present_file = filename
        self._file_count += 1
        
        self.send('--' + self.BOUNDARY + self.CRLF )
        self.send('Content-Disposition: form-data; name="%s"; filename="%s"' % ("file-%d"%(self._file_count), filename) + self.CRLF)
        self.send('Content-Type: %s' % self.get_content_type(filename) + self.CRLF)
        self.send(self.CRLF)
        
        self.flush()
        
    def file_data(self, data):
        assert self._present_file != None
         
        self.send(data)
        self.flush()
         
    def end_file(self):
        assert self._present_file != None
        self._present_file = None
         
        self.send(self.CRLF)
        self.flush()
         
    def end_connection(self):
        self.send('--' + self.BOUNDARY + '--' + self.CRLF)
        self.send(self.CRLF)
        self.flush()
        self.stream.send("0\r\n\r\n\r\n")
