# -*- coding: utf-8 -*-

from django.utils import unittest as unittest
from django.test.client import Client
from django.contrib.auth.models import User as DjangoUser
from yabiadmin.yabi.models import UserProfile

from django.contrib.auth.models import User as DjangoUser
from yabiadmin.yabi.models import Credential, User

class StatusPageTest(unittest.TestCase):
    def test_status_page(self):
        client = Client()
        response = client.get('/status_page')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Status OK" in response.content)

class CreateUserFromAdminTest(unittest.TestCase):
    TEST_USER = 'a_test_user'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        DjangoUser.objects.filter(username=self.TEST_USER).delete()

    # TODO refactor when we add more tests
    def login_admin(self):
        response = self.client.post('/admin/', 
                {'username': 'admin', 'password': 'admin', 
                 'this_is_the_login_form': 1, 'next': '/admin'})
        # This assert might be a bit fragile
        assert response.status_code == 302, "Couldn't log in admin user"

    def test_user_creation(self):
        self.login_admin()
        response = self.client.post('/admin/auth/user/add/',
                {'username': self.TEST_USER, 'password1': 'test', 'password2': 'test', '_save': 'Save'})
        self.assertEqual(response.status_code, 302, 'Should redirect to User List page')
        self.assertTrue(DjangoUser.objects.filter(username=self.TEST_USER).exists(), 'Should create Django User')
        self.assertTrue(UserProfile.objects.filter(user__username=self.TEST_USER).exists(), 'Should create User Profile for user')

class CredentialTests(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create(name=u'győzike')
        self.django_user = DjangoUser.objects.create(username=u'győzike')
        self.django_user.set_password('pass')
        self.django_user.save()
        self.credential = Credential.objects.create(description='null credential', username=self.user.name, user=self.user)

    def tearDown(self):
        self.credential.clear_cache()
        self.credential.delete()
        self.user.delete()
        self.django_user.delete()

    def test_cache_keyname_replaces_unicode_character(self):
        self.assertTrue('\xc5\x91' in self.credential.cache_keyname())

    def test_not_cached(self):
        self.assertFalse(self.credential.is_cached)

    def test_cache(self):
        self.credential.send_to_cache()
        self.assertTrue(self.credential.is_cached)
        self.assertEqual(self.credential.get_from_cache(), None)

    def test_get_from_cache(self):
        self.credential.password = 'pass'
        self.credential.send_to_cache()
        self.credential.password = 'pass2'
        self.credential.get_from_cache()
        self.assertEqual(self.credential.password, 'pass', 'get_from_cache() should set the password back to original')

    def test_clear_from_cache(self):
        self.credential.send_to_cache()
        self.credential.clear_cache()
        self.assertFalse(self.credential.is_cached)

    def test_login_decrypts_credential(self):
        client = Client()
        response = client.post('/wslogin/',
                {'username': self.django_user.username, 'password': 'pass'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.credential.is_cached)


