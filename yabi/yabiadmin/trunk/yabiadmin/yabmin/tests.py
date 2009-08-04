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

        c = Client()
        response = c.get('/ws/tool/blast.xe.ivec.org')
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)

        print payload

