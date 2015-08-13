# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import httplib
import random
import mimetypes
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

    def get_content_type(self, filename):
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
                self.stream.putheader("Cookie", cookie)
        self.stream.putheader('Transfer-Encoding', 'chunked')
        self.stream.putheader('User-Agent', 'YabiUploadStreamer/0.0')
        self.stream.putheader('Expect', '100-continue')
        self.stream.putheader('Accept', '*/*')

        self.stream.endheaders()

    def send(self, string):
        if type(string) is unicode:
            string = str(string)
        self._buff += string

    def flush(self):
        """flush the buffer"""
        self.stream.send(hex(len(self._buff))[2:].upper() + self.CRLF)
        self.stream.send(self._buff)
        self.stream.send(self.CRLF)
        self._buff = ""

    def send_fields(self, fields):
        for (key, value) in fields:
            self.send('--' + self.BOUNDARY + self.CRLF)
            self.send('Content-Disposition: form-data; name="%s"' % key + self.CRLF)
            self.send(self.CRLF)
            self.send(value)
            self.send(self.CRLF)

        self.flush()

    def new_file(self, filename):
        assert self._present_file is None
        self._present_file = filename
        self._file_count += 1

        self.send('--' + self.BOUNDARY + self.CRLF)
        self.send('Content-Disposition: form-data; name="%s"; filename="%s"' % ("file-%d" % (self._file_count), filename) + self.CRLF)
        self.send('Content-Type: %s' % self.get_content_type(filename) + self.CRLF)
        self.send(self.CRLF)

        self.flush()

    def file_data(self, data):
        assert self._present_file is not None

        self.send(data)
        self.flush()

    def end_file(self):
        assert self._present_file is not None
        self._present_file = None

        self.send(self.CRLF)
        self.flush()

    def end_connection(self):
        self.send('--' + self.BOUNDARY + '--' + self.CRLF)
        self.send(self.CRLF)
        self.flush()
        self.stream.send("0\r\n\r\n\r\n")
