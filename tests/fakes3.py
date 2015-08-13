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

from __future__ import print_function
import subprocess
import os
import tempfile
import signal
import shutil
import logging

def fakes3_setup(testcase, bucketname):
    """
    Call this from unittest.TestCase.setUp() to start fakes3.

    The server will be stopped and files deleted when the test case is
    torn down.

    The fakes3 ruby gem needs to be installed for this to work.
    """

    def create_tempdir():
        tmpdir = tempfile.mkdtemp(prefix="s3_connection_tests_")
        testcase.addCleanup(shutil.rmtree, tmpdir)
        return tmpdir

    def start_fakes3(s3dir):
        cmd = ["fakes3", "--root", s3dir, "-p", "8090",
               "--hostname", "localhost.localdomain"]
        out = tempfile.TemporaryFile(suffix=".log", prefix="fakes3-")
        p = subprocess.Popen(cmd, stdin=open("/dev/null"), stdout=out, stderr=out)
        testcase.addCleanup(stop_fakes3, p)
        testcase.addCleanup(show_log, out)

    def stop_fakes3(p):
        os.kill(p.pid, signal.SIGINT)
        p.wait()

    def show_log(logfile):
        logger = logging.getLogger("fakes3")
        logfile.seek(0)
        for line in logfile:
            logger.debug(line)

    s3dir = create_tempdir()
    if bucketname:
        os.mkdir(os.path.join(s3dir, bucketname))
    start_fakes3(s3dir)

    return s3dir
