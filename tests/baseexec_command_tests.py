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

from unittest import TestCase

from yabi.backend.baseexecbackend import BaseExecBackend
from yabi.backend.sshpbsprobackend import SSHPBSProExecBackend
from yabi.backend.sshsgeexecbackend import SSHSGEExecBackend
from yabi.backend.sshtorquebackend import SSHTorqueExecBackend


class BaseCommandsTestCase(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.base_exec_backend = BaseExecBackend()
        self.pbs_backend = SSHPBSProExecBackend()
        self.sge_backend = SSHSGEExecBackend()
        self.torque_backend = SSHTorqueExecBackend()

    def test_command_path_base_exec(self):
        qsub = self.base_exec_backend.get_scheduler_command_path("qsub")
        self.assertEquals(qsub,"qsub","scheduler exec qsub command path wrong: Expected qsub: Actual: %s" % qsub)
        qstat = self.base_exec_backend.get_scheduler_command_path("qstat")
        self.assertEquals(qstat, "qstat","base exec qstat command path wrong: Expected qstat: Actual: %s" % qstat)


    def test_sge_command_paths(self):
        self.skipTest("This tests have to be run on a celery host, they aren't e2e tests")
        qsub = self.sge_backend.get_scheduler_command_path("qsub")
        self.assertEquals(qsub,"/opt/sge6/bin/linux-x64/qsub","sge exec qsub command path wrong: Expected qsub: Actual: %s" % qsub)
        qstat = self.sge_backend.get_scheduler_command_path("qstat")
        self.assertEquals(qstat, "/opt/sge6/bin/linux-x64/qstat","scheduler exec qstat command path wrong: Expected qstat: Actual: %s" % qstat)
        qacct = self.sge_backend.get_scheduler_command_path("qacct")
        self.assertEquals(qacct, "/opt/sge6/bin/linux-x64/qacct","scheduler exec qacct command path wrong: Expected qstat: Actual: %s" % qacct)


    def test_pbs_command_paths(self):
        self.skipTest("This tests have to be run on a celery host, they aren't e2e tests")
        qsub = self.pbs_backend.get_scheduler_command_path("qsub")
        self.assertEquals(qsub,"qsub","pbs exec qsub command path wrong: Expected qsub: Actual: %s" % qsub)
        qstat = self.pbs_backend.get_scheduler_command_path("qstat")
        self.assertEquals(qstat, "qstat" ,"pbs exec qstat command path wrong: Expected qstat: Actual: %s" % qstat)

    def test_torque_command_paths(self):
        self.skipTest("This tests have to be run on a celery host, they aren't e2e tests")
        qsub = self.torque_backend.get_scheduler_command_path("qsub")
        self.assertEquals(qsub,"/opt/torque/2.3.13/bin/qsub","torque  qsub command path wrong: Expected:/opt/torque/2.3.13/bin/qsub Actual: [%s]" % qsub)
        qstat = self.torque_backend.get_scheduler_command_path("qstat")
        self.assertEquals(qstat, "/opt/torque/2.3.13/bin/qstat", "torque exec qstat command path wrong: Expected qstat: Actual: %s" % qstat)

