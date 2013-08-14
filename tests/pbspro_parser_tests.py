import unittest
from yabiadmin.backend.pbsproparsers import *


class QSubParseTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = PBSProParser()
        self.good_lines = ["1223.epic\n", "dontcare\n", "dontcare more\n"]

    def test_qsub_parser_picks_up_remote_id(self):
        result = self.parser.parse_qsub(self.good_lines, [])
        self.assertTrue(result.remote_id == "1223", "PBSProParser failed to parse qsub remote id: Expected: 1223 Actual: %s" % result.remote_id)
        self.assertTrue(result.status == PBSProQSubResult.JOB_SUBMITTED, "PBSProParser qsub result has incorrect status: Expected: %s Actual %s" % (PBSProQSubResult.JOB_SUBMITTED, result.status))

