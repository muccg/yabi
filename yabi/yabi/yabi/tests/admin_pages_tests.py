# -*- coding: utf-8 -*-

import unittest
from django.test.client import Client
from django.contrib.auth.models import User as DjangoUser
from yabi.yabi.models import User
from yabi.yabi.forms import BackendForm


class CreateUserFromAdminTest(unittest.TestCase):
    TEST_USER = 'a_test_user'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        DjangoUser.objects.filter(username=self.TEST_USER).delete()

    # TODO refactor when we add more tests
    def login_admin(self):
        response = self.client.post('/admin-pane/', {
            'username': 'admin', 'password': 'admin',
            'this_is_the_login_form': 1, 'next': '/admin-pane/'})
        # This assert might be a bit fragile
        assert response.status_code == 302, "Couldn't log in admin user"

    def test_user_creation(self):
        self.login_admin()
        response = self.client.post('/admin-pane/auth/user/add/', {
            'username': self.TEST_USER, 'password1': 'test', 'password2': 'test', '_save': 'Save'})
        self.assertEqual(response.status_code, 302, 'Should redirect to User List page')
        self.assertTrue(DjangoUser.objects.filter(username=self.TEST_USER).exists(), 'Should create Django User')
        self.assertTrue(User.objects.filter(user__username=self.TEST_USER).exists(), 'Should create User Profile for user')


class TestBackendFormValidation(unittest.TestCase):
    def setUp(self):
        pass

    def minimal_valid_data(self):
        return {
            "name": "some name",
            "scheme": "sftp",
            "hostname": "ahostname",
            "path": "/a/path/"
        }

    def test_should_be_valid_with_minimal_data(self):
        form = BackendForm(self.minimal_valid_data())
        self.assertTrue(form.is_valid(), "Form should be valid")

    def test_mandatory_fields_are_required(self):
        mandatory_fields = ('name', 'scheme', 'hostname', 'path',)

        def field_is_required_error(field, errors):
            return errors.get(field) == [u'This field is required.']

        form = BackendForm({})
        self.assertFalse(form.is_valid(), "Form shouldn't be valid")
        for mand_field in mandatory_fields:
            self.assertTrue(field_is_required_error(mand_field, form.errors),
                            "Field '%s' should be reported as required" % mand_field)

    def test_scheme_is_a_valid_scheme(self):
        data = self.minimal_valid_data()
        data['scheme'] = "not valid"
        form = BackendForm(data)
        self.assertFalse(form.is_valid(), "Form shouldn't be valid")
        self.assertRegexpMatches(form.errors['scheme'][0], r"^Scheme not valid. Options: ")

    def test_path_should_start_with_slash(self):
        data = self.minimal_valid_data()
        data['path'] = "no/slash/at/start/"
        form = BackendForm(data)
        self.assertFalse(form.is_valid(), "Form shouldn't be valid")
        self.assertEqual(form.errors['path'][0], u"Path must start with a /.")

    def test_path_should_end_with_slash(self):
        data = self.minimal_valid_data()
        data['path'] = "/no/slash/at/end"
        form = BackendForm(data)
        self.assertFalse(form.is_valid(), "Form shouldn't be valid")
        self.assertEqual(form.errors['path'][0], u"Path must end with a /.")

    def test_hostname_can_not_end_in_slash(self):
        data = self.minimal_valid_data()
        data['hostname'] = "hostname-ending-in/"
        form = BackendForm(data)
        self.assertFalse(form.is_valid(), "Form shouldn't be valid")
        self.assertEqual(form.errors['hostname'][0], u"Hostname must not end with a /.")

    def test_lcopy_unsupported_on_s3(self):
        data = self.minimal_valid_data()
        data['scheme'] = "s3"
        data['lcopy_supported'] = True
        form = BackendForm(data)
        self.assertFalse(form.is_valid(), "Form shouldn't be valid")
        self.assertEqual(form.errors['lcopy_supported'][0], u"Local Copy not supported on s3.")

    def test_link_unsupported_on_s3(self):
        data = self.minimal_valid_data()
        data['scheme'] = "s3"
        data['link_supported'] = True
        form = BackendForm(data)
        self.assertFalse(form.is_valid(), "Form shouldn't be valid")
        self.assertEqual(form.errors['link_supported'][0], u"Linking not supported on s3.")
