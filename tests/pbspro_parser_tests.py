import unittest
from yabiadmin.backend.pbsproparsers import PBSProQStatResult, PBSProParser, PBSProQSubResult
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


class QSubParseTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = PBSProParser()
        self.good_lines = ["1223.epic\n", "dontcare\n", "dontcare more\n"]
        self.missing_script_lines_error_lines = ["qsub: script file:: No such file or directory\n"]

    def test_qsub_parser_picks_up_remote_id(self):
        result = self.parser.parse_qsub(self.good_lines, [])
        self.assertTrue(result.remote_id == "1223", "PBSProParser failed to parse qsub remote id: Expected: 1223 Actual: %s" % result.remote_id)
        self.assertTrue(result.status == PBSProQSubResult.JOB_SUBMITTED, "PBSProParser qsub result has incorrect status: Expected: %s Actual %s" % (PBSProQSubResult.JOB_SUBMITTED, result.status))

    def test_qsub_parser_returns_error_status_when_no_such_script(self):
        result = self.parser.parse_qsub([],self.missing_script_lines_error_lines)
        self.assertTrue(result.remote_id is None,"PBSProParser qsub test for missing script - should not assign remote id: Expected: None Actual: %s" % result.remote_id)
        self.assertTrue(result.status == PBSProQSubResult.JOB_SUBMISSION_ERROR,"PBSProParser qsub for missing script. Expected: %s Actual: %s" % (PBSProQSubResult.JOB_SUBMISSION_ERROR, result.status))

class QStatParseTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = PBSProParser()
        self.queued_job_lines = ["Job id            Name             User              Time Use S Queue\n",
                                    "----------------  ---------------- ----------------  -------- - -----\n",
                                    "3485900.epic      test.sh          bioflow           00:00:05 Q debugq\n"]

        self.running_job_lines = ["Job id            Name             User              Time Use S Queue\n",
                                    "----------------  ---------------- ----------------  -------- - -----\n",
                                    "3485900.epic      test.sh          bioflow           00:00:05 R debugq\n"]


        self.completed_job_lines = ["Job id            Name             User              Time Use S Queue\n",
                                    "----------------  ---------------- ----------------  -------- - -----\n",
                                    "3485900.epic      test.sh          bioflow           00:00:05 F debugq\n"]



    def test_qstat_finds_completed_job(self):
        result = self.parser.parse_qstat("3485900", self.completed_job_lines, [])
        self.assertTrue(result.status == PBSProQStatResult.JOB_SUCCEEDED,
                        "PBSProParser failed to report a completed job. Expected status: %s Actual: %s"
                        % (PBSProQStatResult.JOB_SUCCEEDED, result.status))

    def test_qstat_queued_job(self):
        result = self.parser.parse_qstat("3485900", self.queued_job_lines, [])
        self.assertTrue(result.status == PBSProQStatResult.JOB_RUNNING,
                        "PBSProParser failed to report a queued job: Expected %s Actual: %s" % (PBSProQStatResult.JOB_RUNNING, result.status))

    def test_qstat_running_job(self):
        result = self.parser.parse_qstat("3485900", self.running_job_lines, [])
        self.assertTrue(result.status == PBSProQStatResult.JOB_RUNNING,
                        "PBSProParser failed to report a running job: Expected %s Actual: %s" % (PBSProQStatResult.JOB_RUNNING, result.status))
