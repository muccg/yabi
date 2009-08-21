import unittest
from django.test import TestCase
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

    def testInvalidTool(self):
        # test non-existant to ensure we don't explode app
        c = Client()
        response = c.get('/ws/tool/testingtool_thisshouldnotexist')
        self.assertEqual(response.status_code, 404)


    def testMenu(self):

        # get menu for andrew
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


    def testInvalidMenu(self):
        # test non-existant user to ensure we don't explode app
        # menu is set up to return empty json structure but not
        # return 404 so it does not break front end
        c = Client()
        response = c.get('/ws/menu/testingtool_thisshouldnotexist')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["menu"]["toolsets"], [])        



    def testCredential(self):

        # get credential for andrew
        c = Client()
        response = c.get('/ws/credential/andrew/gridftp1')
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertEqual(payload["username"], "amacgregor")
        self.assertEqual(payload["backend"], "gridftp1")


    def testInvalidCredential(self):
        c = Client()
        response = c.get('/ws/credential/testing_this_should_fail/gridftp1')
        self.assertEqual(response.status_code, 404)


    def testCredentialDetailCert(self):
        c = Client()
        response = c.get('/ws/credential/andrew/gridftp1/cert')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("-----BEGIN CERTIFICATE-----" in response.content)


    def testCredentialDetailKey(self):
        c = Client()
        response = c.get('/ws/credential/andrew/gridftp1/key')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("-----BEGIN RSA PRIVATE KEY-----" in response.content)


    def testCredentialDetailUsername(self):
        c = Client()
        response = c.get('/ws/credential/andrew/gridftp1/username')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("amacgregor" in response.content)

