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

        payload = json.loads(response.content)
        toolset = payload["menu"]["toolsets"][0]
        toolgroup = toolset["toolgroups"][0]
        tool = toolgroup["tools"][0]        

        self.assertEqual(toolset["name"], "dev")
        self.assertEqual(toolgroup["name"], "blast")
        self.assertEqual(tool["name"], "blast.xe.ivec.org")
        self.assertEqual(tool["displayName"], "blast")
        self.assertEqual(tool["outputExtensions"][0], "bls")
        self.assertEqual(tool["inputExtensions"][0], "fa")        

        # test non-existant user to ensure we don't explode app
        # menu is set up to return empty json structure but not
        # return 404 so it does not break front end
        response = c.get('/ws/menu/testingtool_thisshouldnotexist')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["menu"]["toolsets"], [])        


