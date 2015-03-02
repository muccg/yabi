from __future__ import print_function
import unittest
from .support import YabiTestCase, StatusResult, all_items, json_path
from .fixture_helpers import admin
import os
import time
from yabi.yabi import models
from socket import gethostname

from model_mommy import mommy


class HostnameTest(YabiTestCase):

    def setUp(self):
        YabiTestCase.setUp(self)
        admin.add_tool_to_all_tools('hostname')

    def tearDown(self):
        YabiTestCase.tearDown(self)
        admin.remove_tool_from_all_tools('hostname')

    def test_hostname(self):
        result = self.yabi.run(['hostname'])
        # AH TODO FIXME do we know hostname?
        #self.assertTrue(gethostname() in result.stdout)
        self.assertTrue(result.stdout)
        result = StatusResult(self.yabi.run(['status', result.id]))
        self.assertEqual(result.workflow.status, 'complete')

    def test_submit_json_directly(self):
        result = self.yabi.run(['submitworkflow', json_path('hostname')])
	# AH TODO FIXME do we know hostname?
        #self.assertTrue(gethostname() in result.stdout)
        self.assertTrue(result.stdout)

    def test_submit_json_directly_larger_workflow(self):
        result = self.yabi.run(['submitworkflow', json_path('hostname_hundred_times')])
        # doesn't cause problems with this
        #result = self.yabi.run(['submitworkflow', json_path('hostname_five_times')])
        wfl_id = result.id

        result = StatusResult(self.yabi.run(['status', wfl_id]))

        print(result.status)
        print(result.workflow)

        self.assertEqual(result.workflow.status, 'complete')
        self.assertTrue(all_items(lambda j: j.status == 'complete', result.workflow.jobs))


class LocalExecutionRedirectTest(YabiTestCase):

    def setUp(self):
        YabiTestCase.setUp(self)
        admin.add_tool_to_all_tools('hostname')
        hostname = models.ToolDesc.objects.get(name='hostname')
        switch_use_redirect = models.ParameterSwitchUse.objects.get(display_text='redirect')
        mommy.make('ToolParameter', tool=hostname, switch='--redirectTo', switch_use=switch_use_redirect, rank=101, output_file=True, file_assignment='none')

    def tearDown(self):
        YabiTestCase.tearDown(self)
        admin.remove_tool_from_all_tools('hostname')

    def test_hostname(self):
        REDIRECT_TO_FILENAME = 'hostname_output.txt'

        result = self.yabi.run(['hostname', '--redirectTo', REDIRECT_TO_FILENAME])

        result = StatusResult(self.yabi.run(['status', result.id]))
        self.assertEqual(result.workflow.status, 'complete', 'Workflow should run to completion')
        self.assertTrue(os.path.isfile(REDIRECT_TO_FILENAME), 'file we redirected to should exist')
        contents = ''
        with open(REDIRECT_TO_FILENAME) as f:
            contents = f.read()
        self.assertTrue(('ssh' in contents) or ('celery' in contents), "The hostname should be in the file we redirected to")


class ExplodingBackendTest(YabiTestCase):

    def setUp(self):
        YabiTestCase.setUp(self)

        # hostname is already in the db, so remove it and re-add to exploding backend
        models.Tool.objects.get(desc__name='hostname').delete()

        admin.create_exploding_backend()
        admin.create_tool('hostname', ex_backend_name='Exploding Backend')
        admin.add_tool_to_all_tools('hostname')

    def tearDown(self):
        models.Tool.objects.get(desc__name='hostname').delete()
        models.Backend.objects.get(name='Exploding Backend').delete()

        # put normal hostname back to restore order
        admin.create_tool('hostname')
        YabiTestCase.tearDown(self)

    # TODO re-enable when we will have an Exploding Backend
    def xtest_submit_json_directly_larger_workflow(self):
        result = self.yabi.run(['submitworkflow', '--backend', 'Exploding Backend',
                                json_path('hostname_hundred_times')])
        wfl_id = result.id
        all_jobs_finished = False
        while not all_jobs_finished:
            result = StatusResult(self.yabi.run(['status', wfl_id]))
            all_jobs_finished = all_items(lambda j: j.status in ('error', 'complete'), result.workflow.jobs)
            time.sleep(2)

        self.assertEqual(result.workflow.status, 'error')
        self.assertTrue(all_items(lambda j: j.status == 'error', result.workflow.jobs))
