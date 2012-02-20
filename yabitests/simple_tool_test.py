from support import YabiTestCase

class HostnameTest(YabiTestCase):
    @classmethod
    def setUpAdmin(self):
        from yabiadmin.yabi import models
        lfs = models.Backend.objects.get(name='Local Filesystem')
        lex = models.Backend.objects.get(name='Local Execution')
        hostname = models.Tool.objects.create(name='hostname', display_name='hostname', path='hostname', backend=lex, fs_backend=lfs)
        tg = models.ToolGroup.objects.get(name='select data')
        alltools = models.ToolSet.objects.get(name='alltools')
        tg.toolgrouping_set.create(tool=hostname, tool_set=alltools)

    @classmethod
    def tearDownAdmin(self):
        from yabiadmin.yabi import models
        models.Tool.objects.get(name='hostname').delete()

    def test_hostname(self):
        from socket import gethostname
        result = self.yabi.run('hostname')
        self.assertTrue(gethostname() in result.stdout)

