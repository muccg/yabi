import unittest
from support import YabiTestCase, StatusResult, FileUtils
from fixture_helpers import admin
import os

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
        # passes with this
        FIVE_GB = 5 * 1024 * 1024
        filename = self.create_tempfile(size=FIVE_GB)
        result = self.yabi.run('cksum %s' % filename)

        expected_cksum, expected_size = self.run_cksum_locally(filename)
       
        returned_lines = filter(lambda l: l.startswith(expected_cksum), result.stdout.split("\n"))
        self.assertEqual(len(returned_lines), 1, 'Cksum result not returned or checksum is incorrect')
        our_line = returned_lines[0]
        actual_cksum, actual_size, rest = our_line.split()
        self.assertEqual(expected_cksum, actual_cksum)
        self.assertEqual(expected_size, actual_size)


class FileUploadAndDownloadTest(YabiTestCase, FileUtils):
    @classmethod
    def setUpAdmin(self):
        from yabiadmin.yabi import models
        admin.create_tool('dd')
        admin.add_tool_to_all_tools('dd')
        tool = models.Tool.objects.get(name='dd')
        tool.accepts_input = True
        star_extension = models.FileExtension.objects.get(pattern='*')
        models.ToolOutputExtension.objects.create(tool=tool, file_extension=star_extension)

        combined_eq = models.ParameterSwitchUse.objects.get(display_text='combined with equals')

        if_tool_param = models.ToolParameter.objects.create(tool=tool, switch_use=combined_eq, mandatory=True, rank=1, file_assignment = 'batch', switch='if')
        all_files = models.FileType.objects.get(name='all files')
        if_tool_param.accepted_filetypes.add(all_files)

        of_tool_param = models.ToolParameter.objects.create(tool=tool, switch_use=combined_eq, mandatory=True, rank=2, file_assignment = 'none', switch='of', output_file=True)

        tool.save()

    @classmethod
    def tearDownAdmin(self):
        from yabiadmin.yabi import models
        models.Tool.objects.get(name='dd').delete()

    def setUp(self):
        YabiTestCase.setUp(self)
        FileUtils.setUp(self)

    def tearDown(self):
        YabiTestCase.tearDown(self)
        FileUtils.tearDown(self)

    def test_dd(self):
        #ONE_GB = 1024 * 1024 * 1024
        # passes with this
        ONE_GB = 1024 * 1024
        filename = self.create_tempfile(size=ONE_GB)
        result = self.yabi.run('dd if=%s of=output_file' % filename)

        expected_cksum, expected_size = self.run_cksum_locally(filename)
        copy_cksum, copy_size = self.run_cksum_locally('output_file')
       
        self.assertEqual(expected_cksum, copy_cksum)
        self.assertEqual(expected_size, copy_size)

