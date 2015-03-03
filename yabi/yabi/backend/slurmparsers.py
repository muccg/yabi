import logging
import re

logger = logging.getLogger(__name__)


class SlurmSubResult(object):
    JOB_SUBMITTED = "job submitted"
    JOB_SUBMISSION_ERROR = "job submission error"

    def __init__(self):
        self.status = None
        self.remote_id = None

    def __repr__(self):
        return "sub result: remote id = %s remote job status = %s" % (self.remote_id, self.status)


class SlurmStatResult(object):
    JOB_RUNNING = "job running"
    JOB_NOT_FOUND = "job not found by stat"

    def __init__(self):
        self.status = None
        self.remote_id = None

    def __repr__(self):
        return "stat result: remote id = %s remote job status = %s" % (self.remote_id, self.status)


class SlurmAcctResult(object):
    JOB_COMPLETED = "job succeeded"
    JOB_NOT_FOUND = "job not found by acct"

    def __init__(self):
        self.status = None
        self.remote_id = None
        self.job_exit_status = None

    def __repr__(self):
        return "acct result: remote id = %s remote job status = %s exit status = %s" % (self.remote_id, self.status, self.job_exit_status)


class SlurmCancelResult(object):
    JOB_ABORTED = "JOB ABORTED"
    JOB_ABORTION_ERROR = "JOB ABORTION ERROR"
    JOB_FINISHED = "JOB FINISHED"

    def __init__(self, status=None, error=None):
        self.status = status
        self.error = error

    @classmethod
    def job_aborted(cls):
        return cls(cls.JOB_ABORTED)

    @classmethod
    def job_finished(cls):
        return cls(cls.JOB_FINISHED)

    @classmethod
    def job_abortion_error(cls, error=None):
        return cls(cls.JOB_ABORTION_ERROR, error)


class SlurmParser(object):
    SBATCH_JOB_SUBMITTED_PATTERN = r"Submitted batch job (?P<remote_id>\d+(?:\.\d+-\d+:\d+)?)"
    SQUEUE_JOB_RUNNING_JOB_OUTPUT = r"^\s*(?P<remote_id>\d+)"
    SACCT_JOB_NUMBER = r"(?P<remote_id>\d+)"

    def parse_sub(self, exit_code, stdout, stderr):
        for line in stderr:
            logger.debug("qsub stderr line: %s" % line)
        result = SlurmSubResult()
        logger.debug("starting qsub parse..")
        if exit_code > 0:
            result.status = SlurmSubResult.JOB_SUBMISSION_ERROR
            return result

        for line in stdout:
            logger.debug("parsing qsub stdout line: %s" % line)
            m = re.match(SlurmParser.SBATCH_JOB_SUBMITTED_PATTERN, line)
            if m:
                logger.debug("matched remote id!")
                result.remote_id = m.group("remote_id")
                result.status = SlurmSubResult.JOB_SUBMITTED
                return result

        result.status = SlurmSubResult.JOB_SUBMISSION_ERROR
        logger.debug("parse result = %s" % result)
        return result

    def parse_poll(self, remote_id, exit_code, stdout, stderr):
        result = SlurmStatResult()
        for line in stdout:
            logger.debug("parsing qstat stdout line: %s" % line)
            m = re.match(SlurmParser.SQUEUE_JOB_RUNNING_JOB_OUTPUT, line)
            if m:
                logger.debug("matched remote id!")
                if m.group("remote_id") == remote_id:
                    result.status = result.JOB_RUNNING
                    return result

        result.status = result.JOB_NOT_FOUND
        logger.debug("parse result = %s" % result)
        return result

    def parse_acct(self, remote_id, exit_code, stdout, stderr):
        result = SlurmAcctResult()
        found_job = False
        for line in stdout:
            logger.debug("parsing qacct stdout line: %s" % line)
            m = re.match(SlurmParser.SACCT_JOB_NUMBER, line)
            if m:
                logger.debug("matched job number!")
                if m.group("remote_id") != remote_id:
                    raise Exception("Error parsing qacct result: Expected remote_id %s Actual %s" % (remote_id, m.group("remote_id")))
                else:
                    found_job = True
                    result.remote_id = m.group("remote_id")
                    result.status = SlurmAcctResult.JOB_COMPLETED

        if not found_job:
            result.status = SlurmAcctResult.JOB_NOT_FOUND

        return result

    def parse_abort(self, remote_id, exit_code, stdout, stderr):
        if exit_code == 0:
            return SlurmCancelResult.job_aborted()

        return SlurmCancelResult.job_abortion_error("\n".join(stdout))
