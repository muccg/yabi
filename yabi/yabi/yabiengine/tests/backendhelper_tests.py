from django.utils import unittest as unittest
from model_mommy import mommy
from yabi.yabi import models as m
from yabi.yabiengine import backendhelper as bh
from django.core.exceptions import ObjectDoesNotExist


def delete_models(*args):
    for model in args:
        model.delete()


class FSBECredentialTest(unittest.TestCase):

    def setUp(self):
        demo_user = m.User.objects.get(name='demo')
        self.cred = mommy.make('Credential', user=demo_user, username='be_user')
        self.be = mommy.make('Backend', scheme='sftp', hostname='some.host.com', path="/some/path/")
        self.be_cred = mommy.make('BackendCredential', backend=self.be, credential=self.cred, homedir="user/")
        self.be_cred_specific = mommy.make('BackendCredential', backend=self.be, credential=self.cred, homedir="user/specific/")

    def tearDown(self):
        delete_models(self.be_cred, self.be_cred_specific, self.cred, self.be)

    def test_raises_error_for_execution_scheme(self):
        try:
            bh.get_fs_backendcredential_for_uri("demo", "ssh://be_user@some.host.com/")
        except ValueError as ve:
            # expected
            self.assertIn("Invalid schema", str(ve))
        else:
            self.assertTrue(False, "Should raise ValueError")

    def test_raise_error_if_no_match(self):
        try:
            # Scheme doesn't match
            bh.get_fs_backendcredential_for_uri("demo", "localfs://be_user@some.host.com/some/path/user/specific/file")
        except ObjectDoesNotExist as e:
            # expected
            self.assertIn("Could not find", str(e))
        else:
            self.assertTrue(False, "Should raise ObjectDoesNotExist")

    def test_returns_backend_cred_when_uri_matches(self):
        be_cred = bh.get_fs_backendcredential_for_uri("demo", "sftp://be_user@some.host.com/some/path/user/file")
        self.assertEquals(be_cred, self.be_cred)

    def test_returns_more_specific_backend_cred(self):
        be_cred = bh.get_fs_backendcredential_for_uri("demo", "sftp://be_user@some.host.com/some/path/user/specific/file")
        self.assertEquals(be_cred, self.be_cred_specific)
