from django.utils import unittest as unittest
from django.test.client import Client
from django.contrib.auth.models import User as DjangoUser
from yabiadmin.yabi.models import UserProfile

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

