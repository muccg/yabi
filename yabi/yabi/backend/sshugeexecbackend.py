from yabi.backend.sshsgebasedexecbackend import SSHSGEBasedExecBackend


class SSHUGEExecBackend(SSHSGEBasedExecBackend):
    SCHEDULER_NAME = "uge"
