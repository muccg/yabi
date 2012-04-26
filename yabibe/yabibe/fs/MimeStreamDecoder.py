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
import gevent
import errno

def no_intr(func, *args, **kw):
    while True:
        try:
            res = func(*args, **kw)
            return res
        except (OSError, IOError), e:
            if e.errno == errno.EINTR or e.errno == errno.EAGAIN:
                gevent.sleep()
            else:
                raise
        

import StringIO

BLOCK_FLUSH_SIZE = 65536                            # 64 kb

class MimeStreamDecoder(object):
    """This is my super no memory usage streaming Mime upload decoder"""
    
    def __init__(self):
        self.line_ending=None                   # the EOL characters
        self._carry = ""                        # for subsequent iterations, this is our carry, our unprocessed data
        self.fileopen = None                    # if we are presently writing the data to a file, this is the file
        self.boundary = None                    # the mime boundary market
        self._is_header = False                 # are we parsing a subfiles header?
        self.content_type = "None/None"
        self.bodyline=False
        
        self.datastream = None                  # for saving data segments (not files)
        self.datakeyname = None                 # save the keyname
        self.datavalues = {}                    # storage 
        
        self.bytes_written = 0                  # bytes written to file
        
    def set_boundary(self, boundary):
        self.boundary = boundary
    
    def open_data_stream(self):
        self.bytes_written = 0
        self.datastream = StringIO.StringIO()
    
    def close_data_stream(self):
        #print "DATA",self.datakeyname,"=",self.datastream.getvalue()
        self.datavalues[self.datakeyname]=self.datastream.getvalue()
        self.datastream = None
    
    def open_write_stream(self, filename):
        """Override this to return the file like object"""
        self.bytes_written = 0
        self.fileopen = open(filename,'wb')
    
    def close_write_stream(self):
        """Override this to close the file like object"""
        self.fileopen.close()
        self.fileopen = None
        
    def write_line(self, line):
        if not line:
            return
        no_intr(getattr(self.fileopen or self.datastream,"write"),line)
        self.bytes_written += len(line)
        
    def write_line_ending(self):
        if self.fileopen:
            self.fileopen.write(self.line_ending)
        else:
            self.datastream.write(self.line_ending)
        self.bytes_written += len(self.line_ending)
    
    def guess_line_ending(self, data):
        """from a section of data, try and guess the line ending"""
        if "\r\n" in data:
            self.line_ending = "\r\n"
        elif "\n\r" in data:
            self.line_ending = "\n\r"
        elif "\r" in data:
            self.line_ending = "\r"
        elif "\n" in data:
            self.line_ending = "\n"
        else:
            self.line_ending = None
    
    def parse_content_disposition(self,line):
        print line
        parts = [X.strip() for X in line.split(";")]
        extra = {}
        for part in parts:
            if part.lower().startswith('content-disposition:'):
                assert part.endswith('form-data')
            else:
                if len(part):
                    key,value = part.split('=')
                    extra[key] = value if (value[0]!='"' and value[1]!='"') else value[1:-1]
        
        # open our file write handle
        if 'filename' not in extra:
            #data segment
            self.datakeyname = extra['name']
            self.open_data_stream()
        else:
            self.open_write_stream(extra['filename'])
        
    def parse_content_type(self,line):
        assert line.lower().startswith('content-type:')
        ctype = line.lower().split()[-1]
        self.content_type = ctype
    
    def feed(self,data):
        if data is None:
            return
        
        # try and guess the line ending if we don't know it yet
        if self.line_ending is None:
            self.guess_line_ending(data)
            
        # split our data on line ending if possible
        if self.line_ending is not None:
            lines = (self._carry + data).split(self.line_ending)
            
            for num,line in enumerate(lines[:-1]):
                # parse content
                if self.boundary in line:
                    bounds = line.split(self.boundary)
                    self.bodyline = False
                    assert False not in [X=='--' or X=='' for X in bounds], "Boundary in request is malformed"
                    bound_start, bound_end = [X=="--" for X in bounds]               # bound_end is true for last boundary
                    if not bound_end:
                        # we've got a new openning boundary
                        if self.fileopen:
                            # close the file. this is the inbetween boundary. another file is coming
                            self.close_write_stream()
                            self._is_header = True
                        elif self.datastream:
                            self.close_data_stream()
                            self._is_header = True
                        else:
                            # this is our first boundary
                            self._is_header = True
                    else:
                        # all the boundaries are written. close the stream
                        if self.fileopen:
                            # close the file. this is the inbetween boundary. another file is coming
                            self.close_write_stream()
                            self._is_header = True
                        elif self.datastream:
                            self.close_data_stream()
                            self._is_header = True
                else:
                    if self._is_header:
                        if line.lower().startswith('content-disposition:'):
                            self.parse_content_disposition(line)
                        elif line.lower().startswith('content-type:'):
                            self.parse_content_type(line)
                        elif not len(line):
                            # end of header is signified by blank line
                            self._is_header = False
                        else:
                            # error
                            raise Exception("Malformed MIME subcontent header section")
                        
                    else:
                        # file body
                        if self.bodyline:
                            self.write_line_ending()
                        self.write_line(line)
                        if num<len(lines)-1:
                            self.bodyline = True
            
            self._carry = lines[-1]       
            
            if len(self._carry) > BLOCK_FLUSH_SIZE and not self._is_header:
                if self.bodyline:
                    self.write_line_ending()
                    self.bodyline = False
                self.write_line(self._carry[:BLOCK_FLUSH_SIZE])
                self._carry = self._carry[BLOCK_FLUSH_SIZE:]
            