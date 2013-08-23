from unittest import TestCase
from fixture_helpers import admin
import os
import hashlib
import stat
from yabiadmin.yabiengine.urihelper import uriparse
from yabiadmin.yabi import models
from yabiadmin.backend.filebackend import FileBackend
from yabiadmin.backend.backend import exec_credential
from yabiadmin.backend.localexecbackend import LocalExecBackend
from mockito import *

TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),'test_data')

def iterate(func, n, *args, **kwargs):
    for i in range(n):
        func(*args, **kwargs)


class DynamicTool(object):
    BASE_PATH = '/tmp'

    def __init__(self, name):
        self.name = name
        self.path = os.path.join(self.BASE_PATH, name)
        self.content_file_path = os.path.join(TEST_DATA_PATH, self.name)
        self.content = open(self.content_file_path).read()


    def deploy(self):
        with open(self.path, "w") as script:
            script.write(self.content)

        st = os.stat(self.path)
        os.chmod(self.path, st.st_mode | stat.S_IEXEC)

    def fill(self, template_dictionary):
        from django.template import Template, Context
        self.content = Template(self.content).render(Context(template_dictionary))

    def remove(self):
        self.unregister()
        os.unlink(self.path)

    def register(self):
        self.unregister()
        admin.create_tool(self.name, self.name, self.path)
        admin.add_tool_to_all_tools(self.name)

    def unregister(self):
        admin.remove_tool_from_all_tools(self.name)
        try:
            models.Tool.objects.get(name=self.name).delete()
        except:
            pass


class TestFileBackendIdempotencyTestCase(TestCase):

    def setUp(self):
        self.username = "demo"
        self.task_working_dir_name = "testing"
        self.create_non_idempotent_tool()
        self.task = self.create_mock_task(self.task_working_dir_name)

        self.fs_backend = FileBackend()
        self.fs_backend.yabiusername = self.username
        self.fs_backend.task = self.task

        self.exec_backend = LocalExecBackend()
        self.exec_backend.task = self.task
        self.exec_backend.yabiusername = self.username
        self.exec_backend.cred = exec_credential(self.username, self.task.job.exec_backend)



    def create_mock_stagein(self, filename, task):
        s = mock()
        s.method = "copy"
        src_path = os.path.join("/home/ccg-user/%s" % filename)
        with open(src_path, "w") as stagein_file:
            stagein_file.write("Stage in file %s\n" % filename)
        s.src = "localfs://demo@localhost/home/ccg-user/%s" % filename
        s.dst = "localfs://demo@localhost/home/ccg-user/%s/input/%s" % (task.working_dir, filename)
        return s

    def create_mock_task(self, task_working_dir):
        mock_task = mock()
        mock_task.fsscheme = 'file'
        mock_task.execscheme = 'localex'
        mock_task.working_dir = task_working_dir
        mock_task.command = self.dynamic_tool.path
        mock_task.stageout = "localfs://demo@localhost:None/home/ccg-user"

        stagein1 = self.create_mock_stagein("stagein1", mock_task)
        stagein2 = self.create_mock_stagein("stagein2", mock_task)
        stagein3 = self.create_mock_stagein("stagein3", mock_task)

        when(mock_task).get_stageins().thenReturn([stagein1, stagein2, stagein3])

        mock_job = mock()
        mock_job.exec_backend = "localex://demo@localhost:None/"
        mock_job.fs_backend = "localfs://localhost:None/home/ccg-user/"
        mock_job.module = None
        mock_workflow = mock()
        mock_job.workflow = mock_workflow
        mock_task.job = mock_job
        mock_user = mock()
        mock_user.name = self.username
        mock_workflow.user = mock_user

        return mock_task



    def create_non_idempotent_tool(self):
        """
        Create a tool which when run twice produces a different result as to when it was run once.
        @return: None
        """
        self.tool_name = 'notidempotent'
        self.dynamic_tool = DynamicTool(self.tool_name)
        self.dynamic_tool.fill({"remnant_file_path": os.path.join("/tmp", self.task_working_dir_name,"remnant_file")})
        self.dynamic_tool.deploy()
        self.dynamic_tool.register()
        self.tool = models.Tool.objects.get(name=self.tool_name)


    def get_path_from_uri(self, uri):
        scheme, parts = uriparse(uri)
        return parts.path

    def check_operation_is_idempotent(self, operation, backend):
        backend_operation = getattr(backend, operation)
        backend_operation()
        run_once_map = self.create_file_map(backend)
        iterate(backend_operation, 3)
        run_many_map = self.create_file_map(backend)
        run_once_items = set(run_once_map.items())
        run_many_map_items = set(run_many_map.items())
        the_diff = run_many_map_items - run_once_items
        self.assertTrue(run_once_map == run_many_map, "Operation %s is not idempotent: Differing files from once and many applications: %s" % (backend_operation,the_diff))

    def calculate_md5(self, filepath):
        return hashlib.md5(open(filepath, 'rb').read()).hexdigest()

    def traverse_path(self, top_path):
        for root, dirs, files in os.walk(top_path):
            for f in files:
                filepath = os.path.join(root, f)
                yield filepath


    def traverse_backend(self, backend):
        for filepath in self.traverse_path(self.get_path_from_uri(backend.working_input_dir_uri())):
            yield filepath
        for filepath in self.traverse_path(self.get_path_from_uri(backend.working_dir_uri())):
            yield filepath
        for filepath in self.traverse_path(self.get_path_from_uri((backend.working_output_dir_uri()))):
            yield filepath
        for filepath in self.traverse_path(backend.local_remnants_dir()):
            yield filepath

    def create_file_map(self, backend):
        return dict([(filepath, self.calculate_md5(filepath)) for filepath in self.traverse_backend(backend)])

    def test_stage_in_is_idempotent(self):
        self.check_operation_is_idempotent("stage_in_files", self.fs_backend)

    def test_stage_out_is_idempotent(self):
        self.fs_backend.stage_in_files()
        self.exec_backend.submit_task()
        self.check_operation_is_idempotent("stage_out_files", self.fs_backend)

    def test_submit_task_is_idempotent(self):
        self.fs_backend.stage_in_files()
        self.check_operation_is_idempotent("submit_task", self.exec_backend)

    def tearDown(self):
        self.dynamic_tool.remove()


