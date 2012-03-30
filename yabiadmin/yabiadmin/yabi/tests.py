# -*- coding: utf-8 -*-

from django.utils import unittest as unittest
from django.test.client import Client

from yabiadmin.yabi.models import Credential, User

class StatusPageTest(unittest.TestCase):
    def test_status_page(self):
        client = Client()
        response = client.get('/status_page')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Status OK" in response.content)

class CredentialTests(unittest.TestCase):
    def setUp(self):
        self.credential = Credential.objects.get(description = 'null credential', user__name='demo')

    def tearDown(self):
        self.credential.clear_cache()
        
    def test_not_cached(self):
        self.assertFalse(self.credential.is_cached)

    def test_cache(self):
        self.credential.send_to_cache()
        self.assertTrue(self.credential.is_cached)

    def test_get_from_cache(self):
        self.credential.password = 'pass1'
        self.credential.send_to_cache()
        self.credential.password = 'pass2'
        self.credential.get_from_cache()
        self.assertEqual(self.credential.password, 'pass1')

    def test_clear_from_cache(self):
        self.credential.send_to_cache()
        self.credential.clear_cache()
        self.assertFalse(self.credential.is_cached)

class CredentialUnicodUsernameTests(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create(name=u'győzike')
        self.credential = Credential.objects.create(description='null credential', username=self.user.name, user=self.user)
       
    def test_cache_keyname_replaces_unicode_character(self):
        self.assertTrue('\xc5\x91' in self.credential.cache_keyname())

    def test_cache(self):
        self.credential.send_to_cache()
        self.assertTrue(self.credential.is_cached)
        self.assertEqual(self.credential.get_from_cache(), None)

    def tearDown(self):
        self.credential.clear_cache()
        self.credential.delete()
        self.user.delete()

class LoginCredentialTest(unittest.TestCase):
    def test_login_decrypts_credential(self):
        client = Client()
        credential = Credential.objects.get(description='null credential', user__name='demo')
        response = client.post('/ws/login/', 
                {'username': 'demo', 'password': 'demo'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue("All credentials were successfully decrypted" in response.content)
        self.assertTrue(credential.is_cached)


