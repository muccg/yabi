# -*- coding: utf-8 -*-

import six
from django.utils import unittest as unittest
from django.contrib.auth.models import User as DjangoUser
from yabi.yabi.models import Credential


class CredentialTests(unittest.TestCase):
    def setUp(self):
        self.django_user = DjangoUser.objects.create(username=u'győzike')
        self.django_user.set_password('pass')
        self.django_user.save()
        self.user = self.django_user.get_profile()
        self.credential = Credential.objects.create(description='test cred', username=self.user.name, user=self.user, password='wombles', cert='cheese', key='it')
        self.credential.save()

    def tearDown(self):
        access = self.credential.get_credential_access()
        access.clear_cache()
        self.credential.delete()
        self.django_user.delete()

    def test_credential_states(self):
        self.assertEqual(self.credential.security_state, Credential.PROTECTED)
        # must be able to decrypt a protected credential
        self.credential.get_credential_access().clear_cache()
        decrypted = self.credential.get_credential_access().get()
        self.assertEqual(decrypted, {six.u('cert'): 'cheese', six.u('password'): 'wombles', six.u('key'): 'it'})
        # logging in must encrypt the credential, and also shove a copy of the
        # decrypted and then protected credential into the cache
        self.credential.get_credential_access().clear_cache()
        self.credential.on_login(self.django_user.username, 'pass')
        self.assertEqual(self.credential.security_state, Credential.ENCRYPTED)
        decrypted = self.credential.get_credential_access().get()
        self.assertEqual(decrypted, {six.u('cert'): 'cheese', six.u('password'): 'wombles', six.u('key'): 'it'})
        # and a final login, with the credentials encrypted in the db already
        self.assertEqual(self.credential.security_state, Credential.ENCRYPTED)
        self.credential.get_credential_access().clear_cache()
        self.credential.on_login(self.django_user.username, 'pass')
        decrypted = self.credential.get_credential_access().get()
        self.assertEqual(decrypted, {six.u('cert'): 'cheese', six.u('password'): 'wombles', six.u('key'): 'it'})

    def test_cache_keyname_replaces_unicode_character(self):
        access = self.credential.get_credential_access()
        self.assertTrue('\\xc5\\x91' in access.keyname, access.keyname)

    def test_cache(self):
        access = self.credential.get_credential_access()
        self.assertTrue(access.in_cache)
        self.assertEqual(access.get(), {six.u('cert'): 'cheese', six.u('password'): 'wombles', six.u('key'): 'it'})
