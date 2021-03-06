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

import os
import unittest
from .support import YabiTestCase, StatusResult, FileUtils, all_items, json_path
from .fixture_helpers import admin
import time
from yabi.yabi import models
from yabi.backend.fsbackend import FSBackend
from socket import gethostname
import logging
from tests.support import conf

logger = logging.getLogger(__name__)


class SSHBackend(object):
    def setUp(self):
        admin.create_ssh_backend()
        admin.create_sftp_backend()

    def tearDown(self):
        models.Backend.objects.get(name='SFTP Backend').delete()
        models.Backend.objects.get(name='SSH Backend').delete()


class ManySSHJobsTest(YabiTestCase, SSHBackend):

    def setUp(self):
        YabiTestCase.setUp(self)
        SSHBackend.setUp(self)

        # hostname is already in the db, so remove it and re-add to exploding backend
        models.Tool.objects.get(desc__name='hostname').delete()

        admin.create_tool('hostname', ex_backend_name='SSH Backend')
        admin.add_tool_to_all_tools('hostname')

    def tearDown(self):
        models.Tool.objects.get(desc__name='hostname').delete()

        # put normal hostname back to restore order
        admin.create_tool('hostname')

        SSHBackend.tearDown(self)
        YabiTestCase.tearDown(self)

    def test_submit_json_directly_larger_workflow(self):
        result = self.yabi.run(['submitworkflow', '--backend', 'SSH Backend',
                                json_path('hostname_hundred_times')])
        wfl_id = result.id
        jobs_running = True
        while jobs_running:
            time.sleep(5)
            sresult = StatusResult(self.yabi.run(['status', wfl_id]))
            jobs_running = False
            for job in sresult.workflow.jobs:
                if job.status not in ('complete', 'error'):
                    jobs_running = True
                    break

        self.assertTrue(sresult.workflow.status in ('complete'))
        self.assertTrue(all_items(lambda j: j.status == 'complete', sresult.workflow.jobs))


class SSHFileTransferTest(YabiTestCase, SSHBackend, FileUtils):

    def setUp(self):
        YabiTestCase.setUp(self)
        SSHBackend.setUp(self)
        FileUtils.setUp(self)

        admin.create_tool_dd(fs_backend_name='SFTP Backend', ex_backend_name='SSH Backend')

        # TODO these unicode tests fail on Docker for some reason
        UNICODE_LAMBDA = u'\u03BB'
        PROBLEMATIC_CHARS = '"$\\\'`\t\x01' + UNICODE_LAMBDA
        fname = 'fake_fasta_' + PROBLEMATIC_CHARS
        fname = 'fake_fasta_'
        self.filename = self.create_tempfile(fname_prefix=fname)


    def tearDown(self):
        models.Tool.objects.get(desc__name='dd').delete()
        FileUtils.tearDown(self)
        SSHBackend.tearDown(self)
        YabiTestCase.tearDown(self)

    def test_dd(self):
        result = self.yabi.run(['dd', 'if=%s' % self.filename.encode("utf-8"), 'of=output_file',
                                '--backend', 'SSH Backend'])
        self.assertTrue(result.status == 0, "Yabish command shouldn't return error!")

        expected_cksum, expected_size = self.run_cksum_locally(self.filename)
        copy_cksum, copy_size = self.run_cksum_locally('output_file')
        if os.path.isfile('output_file'):
            os.unlink('output_file')

        self.assertEqual(expected_size, copy_size)
        self.assertEqual(expected_cksum, copy_cksum)


class SFTPPerformanceTest(SSHBackend, FileUtils):

    def setUp(self):
        SSHBackend.setUp(self)
        FileUtils.setUp(self)
        self.username = conf.yabiusername
        self.homedir = os.environ.get('HOME')

    def tearDown(self):
        FileUtils.tearDown(self)
        SSHBackend.tearDown(self)

    def time_copy_of_files(self, file_count):
        """Copies the passed in amount of files from localhost to localhost
        going through SFTP an times how long the copying takes"""

        a_dir = self.create_tempdir(parentdir=self.homedir) + "/"
        target_dir = self.create_tempdir(parentdir=self.homedir) + "/"

        for i in range(file_count):
            self.create_tempfile(parentdir=a_dir)

        cp_start = time.time()
        FSBackend.remote_copy(self.username,
                'localfs://%s@localhost%s' % (self.username, a_dir),
                'sftp://root@sshtest%s/' % (target_dir))
        copy_duration = time.time() - cp_start

        return copy_duration


    def test_one_file_copy_time(self):
        one_file_cp_duration = self.time_copy_of_files(1)
        two_files_cp_duration = self.time_copy_of_files(2)

        logger.debug(one_file_cp_duration)
        logger.debug(two_files_cp_duration)

        self.assertTrue(two_files_cp_duration < 2 * one_file_cp_duration, "Copying 2 files shouldn't take twice as much as copying 1 file")

    def test_many_files_copy_time(self):
        MANY_FILES = 50
        # We can't expect the copy to be exactly calculable
        # We use an acceptable factor for differences in cp times
        # I usually don't like tests that can fail based on external factors
        # but I will leave this test alive for now (TSZ)
        FACTOR = 0.33 # Copying a file over the same connection shouldn
                      # last less than a third of the time of opening
                      # the connection and cp the file

        one_file_cp_duration = self.time_copy_of_files(1)
        many_files_cp_duration = self.time_copy_of_files(MANY_FILES)

        expected = one_file_cp_duration + (MANY_FILES-1) * one_file_cp_duration * FACTOR

        logger.debug(expected)
        logger.debug(many_files_cp_duration)

        self.assertTrue(many_files_cp_duration < expected, "Expected copy of many files to last less than %s seconds but it lasted %s seconds" % (expected, many_files_cp_duration))
