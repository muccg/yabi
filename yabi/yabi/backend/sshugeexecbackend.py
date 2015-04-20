from yabi.backend.sshsgebasedexecbackend import SSHSGEBasedExecBackend
from yabi.backend.sgeparsers import SGEParser


class SSHUGEExecBackend(SSHSGEBasedExecBackend):
    SCHEDULER_NAME = "uge"
