import unittest
from support import YabiTestCase
from fixture_helpers import admin
import os

JSON_DIR = os.path.join(os.getcwd(), 'json_workflows')
def json_path(name):
    return os.path.join(JSON_DIR, name + '.json')

class HostnameTest(YabiTestCase):
    @classmethod
    def setUpAdmin(self):
        admin.create_tool('hostname')
        admin.add_tool_to_all_tools('hostname') 

    @classmethod
    def tearDownAdmin(self):
        from yabiadmin.yabi import models
        models.Tool.objects.get(name='hostname').delete()

    def test_hostname(self):
        from socket import gethostname
        result = self.yabi.run('hostname')
        self.assertTrue(gethostname() in result.stdout)

    def test_submit_json_directly(self):
        from socket import gethostname
        result = self.yabi.run('submitworkflow %s' % json_path('hostname'))
        self.assertTrue(gethostname() in result.stdout)

    def test_submit_json_directly_larger_workflow(self):
        from socket import gethostname
        result = self.yabi.run('submitworkflow %s' % json_path('hostname_ten_times'))
        self.assertTrue(gethostname() in result.stdout)


class ExplodingBackendTest(YabiTestCase):

    @classmethod
    def setUpAdmin(self):
        admin.create_exploding_backend()
        admin.create_tool('hostname', backend_name='Exploding Backend')
        admin.add_tool_to_all_tools('hostname') 

    @classmethod
    def tearDownAdmin(self):
        from yabiadmin.yabi import models
        models.Tool.objects.get(name='hostname').delete()
        models.Backend.objects.get(name='Exploding Backend').delete()

    def test_hostname(self):
        from socket import gethostname
        result = self.yabi.run('hostname')
        self.assertTrue('Error running workflow' in result.stderr)
   
