from unittest import TestCase

from yabiadmin.backend.baseexecbackend import BaseExecBackend
from yabiadmin.backend.sshpbsprobackend import SSHPBSProExecBackend
from yabiadmin.backend.sshsgeexecbackend import SSHSGEExecBackend
from yabiadmin.backend.sshtorquebackend import SSHTorqueExecBackend


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

