from unittest import TestCase

from yabiadmin.backend.qbaseexecbackend import QBaseExecBackend
from yabiadmin.backend.sshpbsprobackend import SSHPBSProExecBackend
from yabiadmin.backend.sshsgeexecbackend import SSHSGEExecBackend
from yabiadmin.backend.sshtorquebackend import SSHTorqueExecBackend


class QBaseCommandsTestCase(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.qbase_exec_backend = QBaseExecBackend()
        self.pbs_backend = SSHPBSProExecBackend()
        self.sge_backend = SSHSGEExecBackend()
        self.torque_backend = SSHTorqueExecBackend()

    def test_command_path_qbase_exec(self):
        qsub = self.qbase_exec_backend.get_scheduler_command_path("qsub")
        self.assertEquals(qsub,"qsub","scheduler exec qsub command path wrong: Expected qsub: Actual: %s" % qsub)
        qstat = self.qbase_exec_backend.get_scheduler_command_path("qstat")
        self.assertEquals(qstat, "qstat","qbase exec qstat command path wrong: Expected qstat: Actual: %s" % qstat)


    def test_sge_command_paths(self):
        qsub = self.sge_backend.get_scheduler_command_path("/opt/sge6/bin/linux-x64/qsub")
        self.assertEquals(qsub,"qsub","sge exec qsub command path wrong: Expected qsub: Actual: %s" % qsub)
        qstat = self.sge_backend.get_scheduler_command_path("/opt/sge6/bin/linux-x64/qstat")
        self.assertEquals(qstat, "qstat","scheduler exec qstat command path wrong: Expected qstat: Actual: %s" % qstat)
        qacct = self.sge_backend.get_scheduler_command_path("/opt/sge6/bin/linux-x64/qacct")
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

