from unittest import TestCase

from yabiadmin.backend.schedulerexecbackend import SchedulerExecBackend
from yabiadmin.backend.sshpbsprobackend import SSHPBSProExecBackend
from yabiadmin.backend.sshsgeexecbackend import SSHSGEExecBackend
from yabiadmin.backend.sshtorquebackend import SSHTorqueExecBackend


class SchedulerCommandsTestCase(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.scheduler_exec_backend = SchedulerExecBackend()
        self.pbs_backend = SSHPBSProExecBackend()
        self.sge_backend = SSHSGEExecBackend()
        self.torque_backend = SSHTorqueExecBackend()

    def test_command_path_scheduler_exec(self):
        qsub = self.scheduler_exec_backend.get_scheduler_command_path("qsub")
        self.assertEquals(qsub,"qsub","scheduler exec qsub command path wrong: Expected qsub: Actual: %s" % qsub)
        qstat = self.scheduler_exec_backend.get_scheduler_command_path("qstat")
        self.assertEquals(qstat, "qstat","scheduler exec qstat command path wrong: Expected qstat: Actual: %s" % qstat)


    def test_sge_command_paths(self):
        qsub = self.sge_backend.get_scheduler_command_path("qsub")
        self.assertEquals(qsub,"qsub","sge exec qsub command path wrong: Expected qsub: Actual: %s" % qsub)
        qstat = self.sge_backend.get_scheduler_command_path("qstat")
        self.assertEquals(qstat, "qstat","scheduler exec qstat command path wrong: Expected qstat: Actual: %s" % qstat)
        qacct = self.sge_backend.get_scheduler_command_path("qacct")
        self.assertEquals(qacct, "qacct","scheduler exec qacct command path wrong: Expected qstat: Actual: %s" % qacct)


    def test_pbs_command_paths(self):
        qsub = self.pbs_backend.get_scheduler_command_path("qsub")
        self.assertEquals(qsub,"qsub","pbs exec qsub command path wrong: Expected qsub: Actual: %s" % qsub)
        qstat = self.pbs_backend.get_scheduler_command_path("qstat")
        self.assertEquals(qstat, "qstat" ,"pbs exec qstat command path wrong: Expected qstat: Actual: %s" % qstat)

    def test_torque_command_paths(self):
        qsub = self.torque_backend.get_scheduler_command_path("qsub")
        self.assertEquals(qsub,"/opt/torque/2.3.13/bin/qsub","torque  qsub command path wrong: Expected:/opt/torque/2.3.13/bin/qsub Actual: [%s]" % qsub)
        qstat = self.torque_backend.get_scheduler_command_path("qstat")
        self.assertEquals(qstat, "/opt/torque/2.3.13/bin/qstat", "torque exec qstat command path wrong: Expected qstat: Actual: %s" % qstat)

