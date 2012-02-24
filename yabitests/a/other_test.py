from yabitests.support import YabiTestCase

class ATestCase(YabiTestCase):
    @classmethod
    def setUpAdmin(self):
        print 'ADMIN'

    def test_nothing(self):
        self.assertTrue(True)
