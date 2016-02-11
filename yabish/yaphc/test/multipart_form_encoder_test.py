from unittest import TestCase
import os
import tempfile

from yaphc.multipart_form_encoder import MultipartFormEncoder

def read_response(response):
    s = ''
    chunk = 10
    data = response.read(chunk)
    while data:
        s += data
        data = response.read(chunk)
    return s

def create_temp_file_with_content(content):
    fid, path = tempfile.mkstemp()
    with os.fdopen(fid, 'w') as f:
        f.write(content)
    return path

class MultipartFormEncoderFieldsOnlyTest(TestCase):
    def setUp(self):
        self.encoder = MultipartFormEncoder()
        self.fields = (
            ('name1','value1'), 
            ('name2','value2')
        )
        self.files_to_delete = tuple()

    def tearDown(self):
        for f in self.files_to_delete:
            os.remove(f)

    def test_fields(self):
        response_obj = self.encoder.encode(self.fields)
        response = read_response(response_obj) 
        self.assertEqual(response,
'------------ThIs_Is_tHe_bouNdaRY_$\r\n' +
'Content-Disposition: form-data; name="name1"\r\n' + 
'\r\n' +
'value1' +
'\r\n' +
'------------ThIs_Is_tHe_bouNdaRY_$\r\n' +
'Content-Disposition: form-data; name="name2"\r\n' +
'\r\n' +
'value2' +
'\r\n' +
'------------ThIs_Is_tHe_bouNdaRY_$--\r\n\r\n')


    def test_fields_and_files(self):
        file1 = create_temp_file_with_content(
"""Test line 1
Test line 2
"""
        )
        file2 = create_temp_file_with_content(
"""TEST LINE
ANOTHER TEST LINE
ONE MORE TEST LINE
"""
        )
        self.files_to_delete = (file1, file2)
        files = (
            ('A file', 'file1.txt', file1),
            ('Another file', 'file2.txt', file2),
        )
        response_obj = self.encoder.encode(self.fields, files)
        response = read_response(response_obj) 
        self.assertEqual(response,
'------------ThIs_Is_tHe_bouNdaRY_$\r\n' +
'Content-Disposition: form-data; name="name1"\r\n' +
'\r\n' +
'value1' +
'\r\n' +
'------------ThIs_Is_tHe_bouNdaRY_$\r\n' +
'Content-Disposition: form-data; name="name2"\r\n' +
'\r\n' +
'value2' +
'\r\n' +
'------------ThIs_Is_tHe_bouNdaRY_$\r\n' +
'Content-Disposition: form-data; name="A file"; filename="file1.txt"\r\n' +
'Content-Type: text/plain\r\n' +
'\r\n' +
'Test line 1\n' +
'Test line 2\n' +
'\r\n' +
'------------ThIs_Is_tHe_bouNdaRY_$\r\n' +
'Content-Disposition: form-data; name="Another file"; filename="file2.txt"\r\n' +
'Content-Type: text/plain\r\n' +
'\r\n' +
'TEST LINE\n' +
'ANOTHER TEST LINE\n' +
'ONE MORE TEST LINE\n' +
'\r\n' +
'------------ThIs_Is_tHe_bouNdaRY_$--\r\n\r\n')

