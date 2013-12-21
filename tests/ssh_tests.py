import os
import unittest
from .support import YabiTestCase, StatusResult, FileUtils, all_items, json_path
from .fixture_helpers import admin
import time
from yabiadmin.yabi import models
from socket import gethostname
import logging

logger = logging.getLogger(__name__)

class SSHBackend(object):
    def setUp(self):
        admin.create_ssh_backend()
        admin.create_sftp_backend()

        key_file = os.path.join(os.path.dirname(__file__), "test_data/yabitests.pub")
        os.system("cat %s >> ~/.ssh/authorized_keys" % key_file)

    def tearDown(self):
        models.Backend.objects.get(name='SFTP Backend').delete()
        models.Backend.objects.get(name='SSH Backend').delete()
        logger.debug(models.Backend.objects.filter(name='SFTP Backend').count())
        logger.debug(models.Backend.objects.filter(name='SSH Backend').count())

        os.system('sed "/yabitest/ D" -i.old ~/.ssh/authorized_keys')


class ManySSHJobsTest(YabiTestCase, SSHBackend):

    def setUp(self):
        YabiTestCase.setUp(self)
        SSHBackend.setUp(self)

        # hostname is already in the db, so remove it and re-add to exploding backend
        models.Tool.objects.get(name='hostname').delete()

        admin.create_tool('hostname', ex_backend_name='SSH Backend')
        admin.add_tool_to_all_tools('hostname')

    def tearDown(self):
        models.Tool.objects.get(name='hostname').delete()

        # put normal hostname back to restore order
        admin.create_tool('hostname')

        SSHBackend.tearDown(self)
        YabiTestCase.tearDown(self)

    def test_submit_json_directly_larger_workflow(self):
        result = self.yabi.run(['submitworkflow', json_path('hostname_hundred_times')])
        wfl_id = result.id
        jobs_running = True
        while jobs_running:
            time.sleep(5)
            sresult = StatusResult(self.yabi.run(['status', wfl_id]))
            jobs_running = False
            for job in sresult.workflow.jobs:
                if job.status not in ('complete', 'error'):
                    jobs_running = True
                    break

        self.assertTrue(sresult.workflow.status in ('complete'))
        self.assertTrue(all_items(lambda j: j.status == 'complete', sresult.workflow.jobs))


class SSHFileTransferTest(YabiTestCase, SSHBackend, FileUtils):

    def setUp(self):
        YabiTestCase.setUp(self)
        logger.debug(models.Backend.objects.filter(name='SFTP Backend').count())
        logger.debug(models.Backend.objects.filter(name='SSH Backend').count())
        SSHBackend.setUp(self)
        FileUtils.setUp(self)

        admin.create_tool_dd(fs_backend_name='SFTP Backend', ex_backend_name='SSH Backend')
        self.filename = self.create_tempfile()

    def tearDown(self):
        models.Tool.objects.get(name='dd').delete()
        FileUtils.tearDown(self)
        SSHBackend.tearDown(self)
        YabiTestCase.tearDown(self)

    def test_dd(self):
        result = self.yabi.run(['dd', 'if=%s' % self.filename, 'of=output_file'])
        self.assertTrue(result.status == 0, "Yabish command shouldn't return error!")

        expected_cksum, expected_size = self.run_cksum_locally(self.filename)
        copy_cksum, copy_size = self.run_cksum_locally('output_file')
        if os.path.isfile('output_file'):
            os.unlink('output_file')

        self.assertEqual(expected_size, copy_size)
        self.assertEqual(expected_cksum, copy_cksum)

