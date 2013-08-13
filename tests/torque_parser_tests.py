import unittest
from yabiadmin.backend.torqueparsers import *

class QStatParseTestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.parser = TorqueParser()
        self.good_qsub_line = "42940.carah.localdomain"
        self.good_qsub_lines = [self.good_qsub_line ]
        self.good_qsub_err = []
        self.good_qstat = """
                            Job Id: 42940.carah.localdomain
                            Job_Name = test.sh
                            Job_Owner = lrender@carah.localdomain
                            resources_used.cput = 00:00:00
                            resources_used.mem = 0kb
                            resources_used.vmem = 0kb
                            resources_used.walltime = 00:00:00
                            job_state = {0}
                            queue = normal
                            server = carah.localdomain
                            Checkpoint = u
                            ctime = Mon Aug 12 15:19:13 2013
                            Error_Path = carah.localdomain:/export/home/tech/lrender/test.sh.e42940
                            exec_host = carah/0
                            Hold_Types = n
                            Join_Path = n
                            Keep_Files = n
                            Mail_Points = a
                            mtime = Mon Aug 12 15:19:43 2013
                            Output_Path = carah.localdomain:/export/home/tech/lrender/test.sh.o42940
                            Priority = 0
                            qtime = Mon Aug 12 15:19:13 2013
                            Rerunable = True
                            Resource_List.nodect = 1
                            Resource_List.nodes = 1
                            Resource_List.walltime = 01:00:00
                            session_id = 16857
                            Variable_List = PBS_O_HOME=/export/home/tech/lrender,PBS_O_LANG=en_AU.UTF-8,PBS_O_LOGNAME=lrender,PBS_O_PATH=/usr/kerberos/bin:/usr/local/bin:/bin:/usr/bin:/opt/torque/2.3.13/bin/:/export/home/tech/lrender/bin,PBS_O_MAIL=/var/spool/mail/lrender,PBS_O_SHELL=/bin/bash,PBS_O_HOST=carah.localdomain,PBS_SERVER=carah,PBS_O_WORKDIR=/export/home/tech/lrender,PBS_O_QUEUE=normal
                            etime = Mon Aug 12 15:19:13 2013
                            exit_status = {1}
                            submit_args = test.sh
                            start_time = Mon Aug 12 15:19:43 2013
                            start_count = 1
                            comp_time = Mon Aug 12 15:19:43 2013
                            """



    def test_job_prefix_is_parsed(self):
        result = self.parser.parse_qsub(self.good_qsub_lines, self.good_qsub_err)
        self.assertTrue(result.remote_id == "42940")
        self.assertTrue(result.status == TorqueQSubResult.JOB_SUBMITTED)

    def test_qstat_completed(self):
        lines = map(string.strip, self.good_qstat.format("C", "0").split("\n"))
        result = self.parser.parse_qstat("42940", lines, [])
        self.assertTrue(result.status == TorqueQStatResult.JOB_COMPLETED, "torque job status not correct.expected '%s' result = %s" % (TorqueQStatResult.JOB_COMPLETED, result))

    def test_qstat_completed_with_error(self):
        lines = map(string.strip, self.good_qstat.format("C", "127").split("\n"))
        result = self.parser.parse_qstat("42940", lines,[])
        self.assertTrue(result.status == TorqueQStatResult.JOB_ERROR, "torque job status not correct. Expected '%s' result = %s" % (TorqueQStatResult.JOB_ERROR, result))

    def test_qstat_job_still_running(self):
        lines = map(string.strip, self.good_qstat.format("Q","dontcare").split("\n"))
        result = self.parser.parse_qstat("42940", lines, [])
        self.assertTrue(result.status == TorqueQStatResult.JOB_RUNNING, "torque job status wrong - expected %s result = %s" % (TorqueQStatResult.JOB_RUNNING, result))








