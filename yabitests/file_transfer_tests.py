import unittest
from support import YabiTestCase, StatusResult
from fixture_helpers import admin
import os

class FileUtils(object):
    def setUp(self):
        self.tempfiles = []

    def tearDown(self):
        for f in self.tempfiles:
            os.unlink(f)

    def create_tempfile(self, size = 1024, parentdir = None):
        import tempfile
        import stat
        import random as rand
        CHUNK_SIZE = 1024
        def data(length, random=False):
            if not random:
                return "a" * length
            data = ""
            for i in range(length):
                data += rand.choice('abcdefghijklmnopqrstuvwxyz')
            return data
        with tempfile.NamedTemporaryFile(prefix='fake_fasta_', suffix='.fa', delete=False) as f:
            chunks = size / CHUNK_SIZE
            remaining = size % CHUNK_SIZE
            for i in range(chunks):
                if i == 0:
                    f.write(data(1024, random=True))
                else:
                    f.write(data(1024))
            f.write(data(remaining,random=True))
        filename = f.name
        
        self.tempfiles.append(filename)
        return filename       

    def run_cksum_locally(self, filename):
        import subprocess
        cmd = subprocess.Popen('cksum %s' % filename, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        status = cmd.wait()
        assert status == 0
        output = cmd.stdout.read()
        our_line = filter(lambda l: filename in l, output.split("\n"))[0]
        expected_cksum, expected_size, rest = our_line.split()
        return expected_cksum, expected_size

   
class FileUploadTest(YabiTestCase, FileUtils):
    @classmethod
    def setUpAdmin(self):
        from yabiadmin.yabi import models
        admin.create_tool('cksum')
        admin.add_tool_to_all_tools('cksum') 
        tool = models.Tool.objects.get(name='cksum')
        tool.accepts_input = True
        star_extension = models.FileExtension.objects.get(pattern='*')
        models.ToolOutputExtension.objects.create(tool=tool, file_extension=star_extension)
        
        value_only = models.ParameterSwitchUse.objects.get(display_text='valueOnly')

        tool_param = models.ToolParameter.objects.create(tool=tool, switch_use=value_only, mandatory=True, rank=99, file_assignment = 'all', switch='files')
        all_files = models.FileType.objects.get(name='all files')
        tool_param.accepted_filetypes.add(all_files)

        tool.save()

    @classmethod
    def tearDownAdmin(self):
        from yabiadmin.yabi import models
        models.Tool.objects.get(name='cksum').delete()

    def setUp(self):
        YabiTestCase.setUp(self)
        FileUtils.setUp(self)

    def tearDown(self):
        YabiTestCase.tearDown(self)
        FileUtils.tearDown(self)

    def test_cksum_of_large_file(self):
        #FIVE_GB = 5 * 1024 * 1024 * 1024
        FIVE_GB = 5 * 1024
        filename = self.create_tempfile(size=FIVE_GB)
        result = self.yabi.run('cksum %s' % filename)

        expected_cksum, expected_size = self.run_cksum_locally(filename)
       
        returned_lines = filter(lambda l: l.startswith(expected_cksum), result.stdout.split("\n"))
        self.assertEqual(len(returned_lines), 1, 'Cksum result not returned or checksum is incorrect')
        our_line = returned_lines[0]
        actual_cksum, actual_size, rest = our_line.split()
        self.assertEqual(expected_cksum, actual_cksum)
        self.assertEqual(expected_size, actual_size)


class FileUploadAndDownloadTest(YabiTestCase):
    @classmethod
    def xxxsetUpAdmin(self):
        from yabiadmin.yabi import models
        admin.create_tool('cksum')
        admin.add_tool_to_all_tools('cksum')
        tool = models.Tool.objects.get(name='cksum')
        tool.accepts_input = True
        star_extension = models.FileExtension.objects.get(pattern='*')
        models.ToolOutputExtension.objects.create(tool=tool, file_extension=star_extension)

        value_only = models.ParameterSwitchUse.objects.get(display_text='valueOnly')

        tool_param = models.ToolParameter.objects.create(tool=tool, switch_use=value_only, mandatory=True, rank=99, file_assignment = 'all', switch='files')
        all_files = models.FileType.objects.get(name='all files')
        tool_param.accepted_filetypes.add(all_files)

        tool.save()

    @classmethod
    def XXXtearDownAdmin(self):
        from yabiadmin.yabi import models
        models.Tool.objects.get(name='cksum').delete()

    def XsetUp(self):
        YabiTestCase.setUp(self)
        FileUtils.setUp(self)

    def XtearDown(self):
        YabiTestCase.tearDown(self)
        FileUtils.tearDown(self)

    def Xtest_dd(self):
        #FIVE_GB = 5 * 1024 * 1024 * 1024
        FIVE_GB = 5 * 1024
        filename = self.create_tempfile(size=FIVE_GB)
        result = self.yabi.run('cksum %s' % filename)

        expected_cksum, expected_size = self.run_cksum_locally(filename)
       
        returned_lines = filter(lambda l: l.startswith(expected_cksum), result.stdout.split("\n"))
        self.assertEqual(len(returned_lines), 1, 'Cksum result not returned or checksum is incorrect')
        our_line = returned_lines[0]
        actual_cksum, actual_size, rest = our_line.split()
        self.assertEqual(expected_cksum, actual_cksum)
        self.assertEqual(expected_size, actual_size)


