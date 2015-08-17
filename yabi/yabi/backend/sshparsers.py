# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import logging
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
