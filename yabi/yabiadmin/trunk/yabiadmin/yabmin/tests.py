import unittest
from django.test.client import Client
from yabiadmin.yabmin.models import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.utils import simplejson as json

class TestYabmin(unittest.TestCase):
    #fixtures = ['test_data.json'] # this does not seem to work

    def setUp(self):

        # change authentication to backend on the fly
        # manual says don't do this, but we are only testing right?
        settings.AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                                            )
        user, created = User.objects.get_or_create(name="testuser")
        if created:
            user.save()
        self.assertNotEqual(user, None)



    def tearDown(self):
        pass


    def testTool(self):

        # test existing tool
        c = Client()
        response = c.get('/ws/tool/blast.xe.ivec.org')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["tool"]["name"], "blast.xe.ivec.org")

        # test non-existant to ensure we don't explode app
        response = c.get('/ws/tool/testingtool_thisshouldnotexist')
        self.assertEqual(response.status_code, 404)


    def testMenu(self):

        ## TODO need to set up some menu items in fixture to test for them

        # test existing tool
        c = Client()
        response = c.get('/ws/menu/andrew')
        self.assertEqual(response.status_code, 200)
        print response.content
##        payload = json.loads(response.content)
##        self.assertEqual(payload["tool"]["name"], "blast.xe.ivec.org")

##        # test non-existant to ensure we don't explode app
##        response = c.get('/ws/tool/testingtool_thisshouldnotexist')
##        self.assertEqual(response.status_code, 404)
