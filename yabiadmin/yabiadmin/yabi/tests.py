# -*- coding: utf-8 -*-

from django.utils import unittest as unittest
from django.test.client import Client
from django.contrib.auth.models import User as DjangoUser
from yabiadmin.yabi.models import User

from django.contrib.auth.models import User as DjangoUser
from yabiadmin.yabi.models import Credential, User, Backend, Tool, ToolSet, ToolGroup
from django.core.cache import cache

from django.utils import simplejson as json

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
        self.assertTrue(User.objects.filter(user__username=self.TEST_USER).exists(), 'Should create User Profile for user')

class CredentialTests(unittest.TestCase):
    def setUp(self):
        self.django_user = DjangoUser.objects.create(username=u'győzike')
        self.django_user.set_password('pass')
        self.django_user.save()
        self.user = self.django_user.get_profile()
        self.credential = Credential.objects.create(description='null credential', username=self.user.name, user=self.user)

    def tearDown(self):
        self.credential.clear_cache()
        self.credential.delete()
        self.django_user.delete()

    def test_cache_keyname_replaces_unicode_character(self):
        self.assertTrue('\xc5\x91' in self.credential.cache_keyname())

    def test_cache(self):
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

class WsMenuTest(unittest.TestCase):
    def setUp(self):
        self.tool = None
        self.client = Client()
        cache.clear()
        self.login_fe('admin')

    def tearDown(self):
        if self.tool:
            ToolSet.objects.get(name='test').delete()
            Tool.objects.get(name='hostname').delete()

    def test_menu_is_returned(self):
        response = self.client.get('/ws/menu/')
        self.assertEqual(response.status_code, 200, 'Should be able to get menu')
        menu = json.loads(response.content)['menu']
        self.assertEqual(len(menu['toolsets']), 1, 'Should have 1 toolset')
        toolset = menu['toolsets'][0]
        self.assertEqual(toolset['name'], 'all_tools', "Toolset should be 'all_tools'")
        tools = toolset['toolgroups'][0]['tools']
        self.assertEqual(len(tools), 1, "Should have 1 tool")
        self.assertEqual(tools[0]['name'],'fileselector')

    def test_menu_is_cached(self):
        first_response = self.client.get('/ws/menu')
        self.tool = self.add_new_tool()
        second_response = self.client.get('/ws/menu')
        self.assertEqual(first_response.content, second_response.content,
            'Should get the same response from cache')

    def test_menu_contains_new_tool(self):
        self.tool = self.add_new_tool()
        cache.clear()
        response = self.client.get('/ws/menu')
        menu = json.loads(response.content)['menu']
        toolset = menu['toolsets'][0]
        tools = toolset['toolgroups'][0]['tools']
        self.assertEqual(len(tools), 2, "Should have 2 tools")
        tool_names = [t['name'] for t in tools]
        self.assertTrue('hostname' in tool_names, 'Should return new tool')

    def test_menu_isnt_returned_from_cache_for_other_user(self):
        self.tool = self.add_new_tool()
        cache.clear()
        admin_menu = self.client.get('/ws/menu')
        self.login_fe('demo')
        demo_menu = self.client.get('/ws/menu')
        self.assertNotEqual(admin_menu.content, demo_menu.content,
            "Shouldn't get the same response from cache")

    def add_new_tool(self):
        null_backend = Backend.objects.get(name='nullbackend')
        hostname = Tool.objects.create(
            name='hostname', display_name='hostname',
            backend=null_backend, fs_backend=null_backend)
        test_tset = ToolSet.objects.create(name='test')
        admin = User.objects.get(name='admin')
        test_tset.users.add(admin)
        select_data = ToolGroup.objects.get(name='select data')
        select_data.toolgrouping_set.create(tool_set=test_tset, tool=hostname)
        return hostname

    def login_fe(self, user, password=None):
        if password is None:
            password = user
        response = self.client.post('/login', 
                {'username': user, 'password': password}) 
        assert response.status_code == 302, "Couldn't log in to FE"


