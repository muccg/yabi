import unittest
from support import YabiTestCase, StatusResult, all_items, json_path
from fixture_helpers import admin
import os
import time
from yabiadmin.yabi import models
from socket import gethostname


class HostnameTest(YabiTestCase):

    def setUp(self):
        YabiTestCase.setUp(self)
        admin.add_tool_to_all_tools('hostname') 

    def tearDown(self):
        YabiTestCase.tearDown(self)
        admin.remove_tool_from_all_tools('hostname') 

    def test_hostname(self):
        result = self.yabi.run(['hostname'])
        self.assertTrue(gethostname() in result.stdout)
        result = StatusResult(self.yabi.run(['status', result.id]))
        self.assertEqual(result.workflow.status, 'complete')

    def test_submit_json_directly(self):
        result = self.yabi.run(['submitworkflow', json_path('hostname')])
        self.assertTrue(gethostname() in result.stdout)

    def test_submit_json_directly_larger_workflow(self):
        result = self.yabi.run(['submitworkflow', json_path('hostname_hundred_times')])
        # doesn't cause problems with this    
        #result = self.yabi.run(['submitworkflow', json_path('hostname_five_times')])
        wfl_id = result.id

        result = StatusResult(self.yabi.run(['status', wfl_id]))

        print result.status
        print result.workflow

        self.assertEqual(result.workflow.status, 'complete')
        self.assertTrue(all_items(lambda j: j.status == 'complete', result.workflow.jobs))


class ExplodingBackendTest(YabiTestCase):

    def setUp(self):
        YabiTestCase.setUp(self)

        # hostname is already in the db, so remove it and re-add to exploding backend
        models.Tool.objects.get(name='hostname').delete()

        admin.create_exploding_backend()
        admin.create_tool('hostname', ex_backend_name='Exploding Backend')
        admin.add_tool_to_all_tools('hostname') 

    def tearDown(self):
        models.Tool.objects.get(name='hostname').delete()
        models.Backend.objects.get(name='Exploding Backend').delete()

        # put normal hostname back to restore order
        admin.create_tool('hostname')
        YabiTestCase.tearDown(self)

    def test_submit_json_directly_larger_workflow(self):
        result = self.yabi.run(['submitworkflow', json_path('hostname_hundred_times')])
        wfl_id = result.id
        all_jobs_finished = False
        while not all_jobs_finished:
            result = StatusResult(self.yabi.run(['status', wfl_id]))
            all_jobs_finished = all_items(lambda j: j.status in ('error', 'complete'), result.workflow.jobs)
            time.sleep(2)

        self.assertEqual(result.workflow.status, 'error')
        self.assertTrue(all_items(lambda j: j.status == 'error', result.workflow.jobs))
