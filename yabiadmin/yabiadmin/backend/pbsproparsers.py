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

# B  Array job has at least one subjob running.
#
# E  Job is exiting after having run.
#
# F  Job is finished.
#
# H  Job is held.
#
# M  Job was moved to another server.
#
# Q  Job is queued.
#
# R  Job is running.
#
# S  Job is suspended.
#
# T  Job is being moved to new location.
#
# U  Cycle-harvesting job is suspended due to keyboard activity.
#
# W  Job is waiting for its submitter-assigned start time to be reached.
#
# X  Subjob has completed execution or has been deleted.


# use qstat -f <jobnumber> while job executing but -x after for historical info


class PBSProQSubResult(object):
    JOB_SUBMITTED = "JOB SUBMITTED"
    JOB_SUBMISSION_ERROR = "JOB SUBMISSION ERROR"

    def __init__(self):
        self.remote_id = None
        self.status = None
        self.error = None

class PBSProQStatResult(object):
    JOB_RUNNING = "JOB RUNNING"
    JOB_NOT_FOUND = "JOB NOT FOUND BY QSTAT"
    JOB_COMPLETED = "JOB COMPLETED"

    def __init__(self):
        self.remote_id = None
        self.status = None



class PBSProParser(object):
    QSUB_OUTPUT = "^(?P<remote_id>\d+)\..*"
    JOB_STATUS_COLUMN_INDEX = 4
    # From Yabi's point of view , it's either running or finished
    POSSIBLE_STATES = ["B","E", "F", "H", "M", "Q", "R", "S", "T", "U", "W", "X"]
    RUNNING_STATES = ["R", "B", "E", "H", "M", "Q", "S" , "T" ,"U", "W" ] # Added exiting(E)  here to ensure we wait till job has actually finished
    FINISHED_STATES = ["F", "C", "X"]

    def parse_qsub(self, stdout, stderr):
        result = PBSProQSubResult()
        if len(stderr) > 0:
            result.status = PBSProQSubResult.JOB_SUBMISSION_ERROR
            result.error = "\n".join(stderr)
            return result

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
        job_prefix = remote_id + "."
        result = PBSProQStatResult()
        result.remote_id = remote_id
        for line in stdout:
            s = line.strip()
            logger.debug("parsing qstat line: %s" % s)
            if s.startswith(job_prefix):
                parts = s.split()
                job_status = parts[self.JOB_STATUS_COLUMN_INDEX]
                logger.debug("job_status = %s" % job_status)
                if job_status not in self.POSSIBLE_STATES:
                    raise Exception("Unknown PBSPro job state %s for remote id %s" % (job_status, remote_id))
                if job_status in self.RUNNING_STATES:
                    result.status = PBSProQStatResult.JOB_RUNNING
                    return result
                elif job_status in self.FINISHED_STATES:
                    result.status = PBSProQStatResult.JOB_COMPLETED
                    return result

        result.status = PBSProQStatResult.JOB_NOT_FOUND
        return result
