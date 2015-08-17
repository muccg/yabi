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

# This tests don't require any data to be set up before running.

import unittest
from .support import YabiTestCase

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
        result = self.yabi.run(['unknown_tool'])
        self.assertTrue('Unknown tool name "unknown_tool"' in result.stderr)
