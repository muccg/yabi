# This tests don't require any data to be set up before running.

import unittest
from support import YabiTestCase

class FirstTest(unittest.TestCase):
    def test_success(self):
        self.assertTrue(True)

class NotLoggedInTest(YabiTestCase):

    def test_run_yabish_no_args(self):
        result = self.yabi.run()
        self.assertTrue('Usage:' in result.stdout)

    def test_unsuccessful_login(self):
        self.assertTrue(not self.yabi.login('tszabo', 'INVALID_PASS'))

    def test_successful_login(self):
        self.assertTrue(self.yabi.login())


class ToolNotSetupTest(YabiTestCase):
    def test_hostname_not_setup(self):
        result = self.yabi.run('hostname')
        self.assertTrue('Unknown tool name "hostname"' in result.stderr)
