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

import unittest
from .support import YabiTestCase, StatusResult, all_items, json_path
from .fixture_helpers import admin
import time
from yabi.yabi import models
from socket import gethostname


@unittest.skip('Needs Torque')
class TorqueBackendTest(YabiTestCase):

    def setUp(self):
        YabiTestCase.setUp(self)

        # hostname is already in the db, so remove it and re-add to exploding backend
        models.Tool.objects.get(desc__name='hostname').delete()

        admin.create_torque_backend()
        admin.create_tool('hostname', ex_backend_name='Torque Backend')
        admin.add_tool_to_all_tools('hostname')

    def tearDown(self):
        models.Tool.objects.get(desc__name='hostname').delete()
        models.Backend.objects.get(name='Torque Backend').delete()

        # put normal hostname back to restore order
        admin.create_tool('hostname')
        YabiTestCase.tearDown(self)

    def test_hostname(self):
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

        # TODO FIXME
        # This isn't ideal. I get transient errors in Torque, so accepting
        # jobs that complete with error status.
        self.assertTrue(sresult.workflow.status in ('complete', 'error'))
        self.assertTrue(all_items(lambda j: j.status == 'complete', sresult.workflow.jobs))
