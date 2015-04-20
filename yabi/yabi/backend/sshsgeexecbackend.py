from yabi.backend.sshsgebasedexecbackend import SSHSGEBasedExecBackend
from yabi.backend.sgeparsers import SGEParser


class SSHSGEExecBackend(SSHSGEBasedExecBackend):
    SCHEDULER_NAME = "sge"
