# -*- coding: utf-8 -*-
import httplib
import random
import mimetypes
from django.core.files.uploadhandler import FileUploadHandler

# for main() testing uncomment the follwoing line
#FileUploadHandler = object

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
        self.stream.endheaders()
    
    def send(self, string):
        if type(string) is unicode:
            string = str(string)
        self._buff += string
            
    def flush(self):
        """flush the buffer"""
        #print "SENDING:",hex(len(self._buff))[2:].upper(),"=",len(self._buff),"bytes"
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
        
def main():
    # http://faramir.localdomain/yabiadmin/cwellington/ws/fs/put?uri=gridftp://cwellington@xe-gt4.ivec.org/scratch/bi01/cwellington/
    host = "faramir.localdomain"
    port = 80
    selector = "/yabiadmin/cwellington/ws/fs/put?uri=gridftp://cwellington@xe-gt4.ivec.org/scratch/bi01/cwellington/"
    
    import random
    dat = "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz ") for X in range(8192*5)])
    
    streamer = UploadStreamer()
    #cookie = "sessionid=6a46a5c7ef1a5b4040ad8181c87871ca"
    cookie = "sessionid=0578372359971e3e2a1565cc382bb1c8"
    streamer.post_multipart(host=host, port=port, selector=selector, cookies=[cookie] )
    
    filename = "zope.interface-3.3.0.tar.gz"
    with open(filename,'rb') as fh:
        data = fh.read()
        
    streamer.new_file(filename)
    streamer.file_data(data[:65170])
    streamer.file_data(data[65170:])
    streamer.end_file()
    streamer.end_connection()
    
    print dir(streamer.stream)
    resp = streamer.stream.getresponse()
    print resp.status,resp.reason
    print resp.read()
    
if __name__=="__main__":
    main()