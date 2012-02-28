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
        FIVE_GB = 5 * 1024 * 1024 * 1024
        # passes with this
        #FIVE_GB = 5 * 1024 * 1024
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
        ONE_GB = 1024 * 1024 * 1024
        # passes with this
        #ONE_GB = 1024 * 1024
        filename = self.create_tempfile(size=ONE_GB)
        result = self.yabi.run('dd if=%s of=output_file' % filename)

        expected_cksum, expected_size = self.run_cksum_locally(filename)
        copy_cksum, copy_size = self.run_cksum_locally('output_file')
       
        self.assertEqual(expected_cksum, copy_cksum)
        self.assertEqual(expected_size, copy_size)

class FileUploadSmallFilesTest(YabiTestCase, FileUtils):
    @classmethod
    def setUpAdmin(self):
        from yabiadmin.yabi import models
        admin.create_tool('tar')
        admin.add_tool_to_all_tools('tar') 
        tool = models.Tool.objects.get(name='tar')
        tool.accepts_input = True
        #star_extension = models.FileExtension.objects.get(pattern='*')
        #models.ToolOutputExtension.objects.create(tool=tool, file_extension=star_extension)
        
        value_only = models.ParameterSwitchUse.objects.get(display_text='valueOnly')
        both = models.ParameterSwitchUse.objects.get(display_text='both')
        switch_only = models.ParameterSwitchUse.objects.get(display_text='switchOnly')

        tool_param_c = models.ToolParameter.objects.create(tool=tool, switch_use=switch_only, file_assignment = 'none', switch='-c')
        tool_param_f = models.ToolParameter.objects.create(tool=tool, switch_use=both, file_assignment = 'none', output_file=True, switch='-f')
        all_files = models.FileType.objects.get(name='all files')
        tool_param_f.accepted_filetypes.add(all_files)
        tool_param_files = models.ToolParameter.objects.create(tool=tool, switch_use=value_only, rank=99, file_assignment = 'all', switch='files')
        tool_param_files.accepted_filetypes.add(all_files)

        tool.save()

    @classmethod
    def tearDownAdmin(self):
        from yabiadmin.yabi import models
        models.Tool.objects.get(name='tar').delete()

    def setUp(self):
        YabiTestCase.setUp(self)
        FileUtils.setUp(self)

    def tearDown(self):
        YabiTestCase.tearDown(self)
        FileUtils.tearDown(self)

    def test_tar_on_a_few_files(self):
        import tarfile
        MB = 1024 * 1024
        dirname = self.create_tempdir() + "/"
        file1 = self.create_tempfile(size=1 * MB, parentdir=dirname)
        file2 = self.create_tempfile(size=2 * MB, parentdir=dirname)
        file3 = self.create_tempfile(size=3 * MB, parentdir=dirname)
        files = dict([(os.path.basename(f), f) for f in (file1, file2, file3)])

        result = self.yabi.run('tar -c -f file_1_2_3.tar %s' % dirname)

        extract_dirname = self.create_tempdir()
        tar = tarfile.TarFile('file_1_2_3.tar')
        tar.extractall(extract_dirname)

        tarfiles = tar.getnames()
        self.assertEqual(len(tarfiles), 3)
        for extracted_f in tarfiles:
            full_name = os.path.join(extract_dirname, extracted_f)
            self.assertTrue(os.path.basename(extracted_f) in files)
            matching_f = files[os.path.basename(extracted_f)]
            self.compare_files(matching_f, full_name)

    def compare_files(self, file1, file2):
        expected_cksum, expected_size = self.run_cksum_locally(file1)
        actual_cksum, actual_size = self.run_cksum_locally(file2)
        self.assertEqual(expected_cksum, actual_cksum)
        self.assertEqual(expected_size, actual_size)

