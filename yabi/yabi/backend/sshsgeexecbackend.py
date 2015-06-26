from yabi.backend.sshsgebasedexecbackend import SSHSGEBasedExecBackend


class SSHSGEExecBackend(SSHSGEBasedExecBackend):
    SCHEDULER_NAME = "sge"
