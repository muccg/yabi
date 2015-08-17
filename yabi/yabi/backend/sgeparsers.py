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

import logging
import re
from functools import partial
from six.moves import filter
from six.moves import map

logger = logging.getLogger(__name__)


class SGEQSubResult(object):
    JOB_SUBMITTED = "job submitted"
    JOB_SUBMISSION_ERROR = "job submission error"

    def __init__(self):
        self.status = None
        self.remote_id = None

    def __repr__(self):
        return "qsub result: remote id = %s remote job status = %s" % (self.remote_id, self.status)


class SGEQStatResult(object):
    JOB_RUNNING = "job running"
    JOB_NOT_FOUND = "job not found by qstat"

    def __init__(self):
        self.status = None
        self.remote_id = None

    def __repr__(self):
        return "qstat result: remote id = %s remote job status = %s" % (self.remote_id, self.status)


class SGEQAcctResult(object):
    JOB_COMPLETED = "job succeeded"
    JOB_NOT_FOUND = "job not found by qacct"

    def __init__(self):
        self.status = None
        self.remote_id = None
        self.job_exit_status = None

    def __repr__(self):
        return "qsub result: remote id = %s remote job status = %s exit status = %s" % (self.remote_id, self.status, self.job_exit_status)


class SGEQDelResult(object):
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


class SGEParser(object):
    QSUB_JOB_SUBMITTED_PATTERN = r"Your job(?:-array)? (?P<remote_id>\d+(?:\.\d+-\d+:\d+)?)"
    ARRAY_JOB_ID_PATTERN = r"^(\d+)\.(\d+)-(\d+):(\d+)$"
    QSTAT_JOB_RUNNING_JOB_OUTPUT = r"job_number:\s+(?P<remote_id>\d+)"
    QACCT_JOB_NUMBER = r"^jobnumber\s+(?P<remote_id>\d+)"
    QACCT_EXIT_STATUS = r"^exit_status\s(?P<exit_status>\d+)"
    QACCT_FAILED = r"^failed\s+(?P<failed>[10])"
    QDEL_JOB_ABORTED = r"has deleted job (?P<remote_id>\d+)"
    QDEL_JOB_ABORT_REGISTERED = r"registered the job (?P<remote_id>\d+) for deletion"
    QDEL_JOB_FINISHED = r'job "(?P<remote_id>\d+)" does not exist'

    def parse_sub(self, exit_code, stdout, stderr):
        for line in stderr:
            logger.debug("qsub stderr line: %s" % line)
        result = SGEQSubResult()
        logger.debug("starting qsub parse..")
        if exit_code > 0:
            result.status = SGEQSubResult.JOB_SUBMISSION_ERROR
            return result

        for line in stdout:
            logger.debug("parsing qsub stdout line: %s" % line)
            m = re.match(SGEParser.QSUB_JOB_SUBMITTED_PATTERN, line)
            if m:
                logger.debug("matched remote id!")
                result.remote_id = m.group("remote_id")
                result.status = SGEQSubResult.JOB_SUBMITTED
                return result

        result.status = SGEQSubResult.JOB_SUBMISSION_ERROR
        logger.debug("parse result = %s" % result)
        return result

    def parse_poll(self, remote_id, exit_code, stdout, stderr):
        match = re.match(SGEParser.ARRAY_JOB_ID_PATTERN, remote_id)
        if match:
            remote_id = match.group(1)

        result = SGEQStatResult()
        for line in stdout:
            logger.debug("parsing qstat stdout line: %s" % line)
            m = re.match(SGEParser.QSTAT_JOB_RUNNING_JOB_OUTPUT, line)
            if m:
                logger.debug("matched remote id!")
                if m.group("remote_id") == remote_id:
                    result.status = result.JOB_RUNNING
                    return result

        result.status = result.JOB_NOT_FOUND
        logger.debug("parse result = %s" % result)
        return result

    def parse_acct(self, remote_id, exit_code, stdout, stderr):
        if re.match(SGEParser.ARRAY_JOB_ID_PATTERN, remote_id):
            return self.parse_array_job_qacct(remote_id, exit_code, stdout, stderr)
        return self.parse_job_qacct(remote_id, exit_code, stdout, stderr)

    def parse_job_qacct(self, remote_id, exit_code, stdout, stderr):
        result = SGEQAcctResult()
        found_job = False
        for line in stdout:
            logger.debug("parsing qacct stdout line: %s" % line)
            m = re.match(SGEParser.QACCT_JOB_NUMBER, line)
            if m:
                logger.debug("matched job number!")
                if m.group("remote_id") != remote_id:
                    raise Exception("Error parsing qacct result: Expected remote_id %s Actual %s" % (remote_id, m.group("remote_id")))
                else:
                    found_job = True
                    result.remote_id = m.group("remote_id")
                    result.status = SGEQAcctResult.JOB_COMPLETED

        if not found_job:
            result.status = SGEQAcctResult.JOB_NOT_FOUND

        return result

    def parse_array_job_qacct(self, remote_id, exit_code, stdout, stderr):
        # For array jobs qacct returns one entry for each subjob separated by
        # "====...===" (62 of them)
        # We parse each subjob output and check that the jobnumber matches, and
        # that all the subjobs had exactly one account record outputed

        result = SGEQAcctResult()
        match = re.match(SGEParser.ARRAY_JOB_ID_PATTERN, remote_id)
        if match is None:
            raise RuntimeError("Remote id '%s' doesn't look like an array job pattern" % remote_id)
        expected_job_id, first_subjob_id, last_subjob_id, step = match.groups()
        expected_subjob_ids = list(range(int(first_subjob_id), int(last_subjob_id) + 1, int(step)))

        all_lines = "".join(stdout)
        SUBJOB_SEPARATOR = "=" * 62 + "\n"

        # One entry for the output of each subjob
        subjob_acct_outputs = all_lines.split(SUBJOB_SEPARATOR)
        subjob_acct_outputs = filter(lambda x: x.strip() != '', subjob_acct_outputs)

        def extract_value(name, s):
            match = re.search(r"^%s\s+(?P<value>\S+)\s*$" % name, s, flags=re.MULTILINE)
            if match:
                return match.group('value')

        returned_job_ids = [extract_value('jobnumber', sj_out) for sj_out in subjob_acct_outputs]
        returned_subjob_ids = [extract_value('taskid', sj_out) for sj_out in subjob_acct_outputs]

        if not returned_job_ids or not returned_subjob_ids:
            result.status = SGEQAcctResult.JOB_NOT_FOUND
            return result

        if not all([ret_job_id == expected_job_id for ret_job_id in returned_job_ids]):
            raise RuntimeError("Not all subjobs returned the jobnumber %s" % expected_job_id)

        if frozenset(expected_subjob_ids) != frozenset(map(lambda x: int(x), returned_subjob_ids)):
            result.status = SGEQAcctResult.JOB_NOT_FOUND
            return result

        result.status = SGEQAcctResult.JOB_COMPLETED
        result.remote_id = remote_id
        return result

    def parse_abort(self, remote_id, exit_code, stdout, stderr):
        # Note: SGE tools print errors to stdout
        if exit_code == 0:
            return SGEQDelResult.job_aborted()

        for line in stdout:
            if job_finished_line(line, remote_id):
                return SGEQDelResult.job_finished()

        return SGEQDelResult.job_abortion_error("\n".join(stdout))


def line_matches(regex, line, remote_id):
    m = re.search(regex, line)
    if m:
        if m.group("remote_id") != remote_id:
            raise Exception("Error parsing qdel result: Expected remote_id %s Actual %s" % (remote_id, m.group("remote_id")))
        return True
    return False

job_aborted_line = partial(line_matches, SGEParser.QDEL_JOB_ABORTED)
job_abort_registered_line = partial(line_matches, SGEParser.QDEL_JOB_ABORT_REGISTERED)
job_finished_line = partial(line_matches, SGEParser.QDEL_JOB_FINISHED)
