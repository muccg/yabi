import re
import logging
import string
logger = logging.getLogger(__name__)


# [bioflow@epicuser1 demo]$ qsub ./test.sh
# 3485900.epic
# [bioflow@epicuser1 demo]$
#
#
# [bioflow@epicuser1 demo]$ qstat -x 3485900
# Job id            Name             User              Time Use S Queue
# ----------------  ---------------- ----------------  -------- - -----
# 3485900.epic      test.sh          bioflow           00:00:05 F debugq
# [bioflow@epicuser1 demo]$

class PBSProQSubResult(object):
    JOB_SUBMITTED = "job submitted"
    JOB_SUBMISSION_ERROR = "job submission error"

    def __init__(self):
        self.remote_id = None
        self.status = None

class PBSProQStatResult(object):
    JOB_RUNNING = "job running"
    JOB_NOT_FOUND = "job not found by qstat"
    JOB_SUCCEEDED = "job succeeded"
    JOB_FAILED = "job error"

    def __init__(self):
        self.remote_id = None
        self.status = None

class PBSProParser(object):
    QSUB_OUTPUT = "^(?P<remote_id>\d+)\..*"

    def parse_qsub(self, stdout, stderr):
        result = PBSProQSubResult()
        for line in stdout:
            s = line.strip()
            m = re.match(self.QSUB_OUTPUT, s)
            if m:
                result.remote_id = m.group("remote_id")
                result.status = PBSProQSubResult.JOB_SUBMITTED
                return result

        result.status = PBSProQSubResult.JOB_SUBMISSION_ERROR
        return result

    def parse_qstat(self, remote_id, stdout, stderr):
        result = PBSProQStatResult()
        return result