import unittest
from support import YabiTestCase, StatusResult, FileUtils, all_items, json_path
from fixture_helpers import admin
import os
import shutil

class RewalkTest(YabiTestCase, FileUtils):
    '''
    This test creates a worflow that dd's a file and then cksum the file produced by dd.
    The cksum will have a dependency on the dd and it will have to be re-walked by Yabi.
    Yabish doesn't support workflows with multiple jobs, so we will have to submit the json directly.
    Furthermore, the we will use has to be created in the /home/dir of the user so that the BE can access it.
    In order to make this all work on different machines/users we will replace variables in the JSON file at run time.
    '''

    @classmethod
    def setUpAdmin(self):
        from yabiadmin.yabi import models
        admin.create_tool_cksum()
        admin.create_tool_dd()

    @classmethod
    def tearDownAdmin(self):
        from yabiadmin.yabi import models
        models.Tool.objects.get(name='cksum').delete()
        models.Tool.objects.get(name='dd').delete()

    def setUp(self):
        YabiTestCase.setUp(self)
        FileUtils.setUp(self)

    def tearDown(self):
        YabiTestCase.tearDown(self)
        FileUtils.tearDown(self)

    def get_localfs_dir(self):
        LOCALFS_PREFIX = 'localfs://demo@localhost'
        result = self.yabi.run('ls')
        assert result.status == 0, "yabi ls returned an error"
        localfs_line = None
        for line in result.stdout.split(os.linesep):
            if line.startswith(LOCALFS_PREFIX):
                localfs_line = line
                break
        assert localfs_line is not None, "didn't find line starting with localfs in output of yabi ls"
        return localfs_line[len(LOCALFS_PREFIX):]

    def prepare_json(self, filename, new_filename, variables):
        '''Takes contents of filename replaces the variables in it and writes it out to new_filename'''
        content = None
        with open(filename) as f:
            content = f.read()

        changed_content = content
        for k,v in variables.items():
            changed_content = changed_content.replace("${%s}" % k, v)

        with open(new_filename, 'w') as f :
            f.write(changed_content)

    def test_dd_file_then_cksum_direct_json(self):
        wfl_json_file = json_path('dd_then_cksum')
        localfs_dir = self.get_localfs_dir()

        ONE_MB = 1024 * 1024
        filename = self.create_tempfile(size=ONE_MB)
        shutil.copy(filename, localfs_dir)
        filename = os.path.join(localfs_dir, os.path.basename(filename))
        self.delete_on_exit(filename)

        changed_json_file = os.path.join(localfs_dir, 'dd_then_cksum.json')
        self.delete_on_exit(changed_json_file)

        self.prepare_json(wfl_json_file, changed_json_file, {
            'DIR': localfs_dir, 'FILENAME': os.path.basename(filename)})

        result = self.yabi.run('submitworkflow %s' % changed_json_file)
        wfl_id = result.id
        result = StatusResult(self.yabi.run('status %s' % wfl_id))
        self.assertEqual(result.workflow.status, 'complete')
        self.assertTrue(all_items(lambda j: j.status == 'complete', result.workflow.jobs))

