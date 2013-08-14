import unittest
from yabiadmin.backend.pbsproparsers import *


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


