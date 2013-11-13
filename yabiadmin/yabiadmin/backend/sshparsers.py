import re
import logging
import string
logger = logging.getLogger(__name__)


class SSHSubmitResult(object):
    JOB_SUBMITTED = "JOB SUBMITTED"
    JOB_SUBMISSION_ERROR = "JOB SUBMISSION ERROR"

    def __init__(self):
        self.remote_id = None
        self.status = None
        self.error = None

class SSHPsResult(object):
    JOB_RUNNING = "JOB RUNNING"
    JOB_NOT_FOUND = "JOB NOT FOUND BY PS"
    JOB_COMPLETED = "JOB COMPLETED"

    def __init__(self):
        self.remote_id = None
        self.status = None



class SSHParser(object):
    SUBMISSION_OUTPUT = "^(?P<remote_id>\d+)"

    def parse_sub(self, exit_code, stdout, stderr):
        result = SSHSubmitResult()

        if exit_code > 0 or len(stderr) > 0:

            result.status = SSHSubmitResult.JOB_SUBMISSION_ERROR
            result.error = "\n".join(stderr)
            logger.debug('Got something in stderr:\n%s', result.error)
            return result

        for line in stdout:
            s = line.strip()
            m = re.match(self.SUBMISSION_OUTPUT, s)
            if m:
                result.remote_id = m.group("remote_id")
                result.status = SSHSubmitResult.JOB_SUBMITTED
                return result

        logger.debug("Didn't match stdout:\n%s", stdout)

        result.status = SSHSubmitResult.JOB_SUBMISSION_ERROR
        return result

    def parse_poll(self, remote_id, exit_code, stdout, stderr):
        result = SSHPsResult()
        result.remote_id = remote_id
        for line in [s.strip() for s in stdout if s.strip() != '']:
            if remote_id == line:
                result.status = SSHPsResult.JOB_RUNNING
                return result

        result.status = SSHPsResult.JOB_COMPLETED
        return result

