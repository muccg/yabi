# -*- coding: utf-8 -*-
import httplib
import random
import mimetypes

class UploadStreamer(object):
    BOUNDARY_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    CRLF = "\r\n"
    
    def __init__(self):
        self._buff = ""
        self._present_file = None
        self._file_count = 0
        self.BOUNDARY = self.encode_multipart_make_boundary()
    
    def encode_multipart_make_boundary(self):
        boundary = "".join([random.choice(self.BOUNDARY_CHARS) for X in range(28)])
        return "--"+boundary+"--"

    def encode_multipart_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.BOUNDARY
    
    def get_content_type(self,filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
    def post_multipart(self, host, port, selector, fields):
        """
        Post fields and files to an http host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return the server's response page.
        """
        #print "post_multipart"
        content_type = self.encode_multipart_content_type()
        
        self.stream = httplib.HTTPConnection(host)
        self.stream.putrequest('POST', selector)
        self.stream.putheader('Content-Type', content_type)
        self.stream.putheader('Transfer-Encoding', 'chunked')
        self.stream.endheaders()
    
    def send(self, string):
        self._buff += string
        
    def flush(self):
        """Actually write the pending data down the connection. Use Chunked encoding to send it"""
        self.stream.send(hex(len(self._buff))[2:].upper()+self.CRLF)
        self.stream.send(self._buff)
        self.stream.send(self.CRLF + self.CRLF)
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
        
def main():
    host = "hydra.nac.uci.edu"
    port = 80
    selector = "/indiv/franklin/cgi-bin/values"
    
    streamer = UploadStreamer()
    streamer.post_multipart(host=host, port=port, selector=selector, fields=[('key','value'),('key2','value2')] )
    streamer.new_file("myfile.txt")
    streamer.file_data("line 1\nline 2\n")
    streamer.file_data("line 3\nline 4\n")
    streamer.file_data("line 5\nline 6\n")
    streamer.end_file()
    streamer.end_connection()
    
    print dir(streamer.stream)
    resp = streamer.stream.getresponse()
    print resp.read()
    
if __name__=="__main__":
    main()