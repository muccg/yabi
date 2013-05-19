import os
import unittest
from support import YabiTestCase, StatusResult, all_items, json_path
from fixture_helpers import admin
import time
from yabiadmin.yabi import models
from socket import gethostname

#
# Please add tests/test_data/yabitests.pub to ~/.ssh/authorized_keys
#

class SSHBackendTest(YabiTestCase):

    def setUp(self):
        YabiTestCase.setUp(self)

        # hostname is already in the db, so remove it and re-add to exploding backend
        models.Tool.objects.get(name='hostname').delete()

        admin.create_ssh_backend()
        admin.create_tool('hostname', ex_backend_name='SSH Backend')
        admin.add_tool_to_all_tools('hostname')

    def tearDown(self):
        models.Tool.objects.get(name='hostname').delete()
        models.Backend.objects.get(name='SSH Backend').delete()

        # put normal hostname back to restore order
        admin.create_tool('hostname')
        YabiTestCase.tearDown(self)

    # This test must run first, it sets up the known hosts
    def test_a_failure_to_get_host_key(self):
        # try and run a command, it will fail due to host key error
        result = self.yabi.run(['hostname'])
        result = StatusResult(self.yabi.run(['status', result.id]))
        self.assertEqual(result.workflow.status, 'error')

        # now lets validate the host key
        hostkey = models.HostKey.objects.get(hostname='localhost')
        hostkey.allowed = True
        hostkey.save()

        # now run hostname again, it will pass
        result = self.yabi.run(['hostname'])
        self.assertTrue(gethostname() in result.stdout)
        result = StatusResult(self.yabi.run(['status', result.id]))
        self.assertEqual(result.workflow.status, 'complete')

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
