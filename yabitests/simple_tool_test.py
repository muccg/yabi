import unittest
from support import YabiTestCase
from fixture_helpers import admin

class HostnameTest(YabiTestCase):
    @classmethod
    def setUpAdmin(self):
        admin.create_tool('hostname')
        admin.add_tool_to_all_tools('hostname') 

    @classmethod
    def tearDownAdmin(self):
        from yabiadmin.yabi import models
        models.Tool.objects.get(name='hostname').delete()

    unittest.skip("while STDOUT, STDERR not returned properly in quickstart")
    def test_hostname(self):
        from socket import gethostname
        result = self.yabi.run('hostname')
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

   

