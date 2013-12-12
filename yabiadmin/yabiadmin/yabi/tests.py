# -*- coding: utf-8 -*-

from django.utils import unittest as unittest
from django.test.client import Client
from django.contrib.auth.models import User as DjangoUser
from yabiadmin.yabi.models import User

from django.contrib.auth.models import User as DjangoUser
from yabiadmin.yabi.models import Credential, User, Backend, Tool, ToolSet, ToolGroup
from django.core.cache import cache

from django.utils import simplejson as json
import six

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
        response = self.client.post('/admin-pane/',
                {'username': 'admin', 'password': 'admin',
                 'this_is_the_login_form': 1, 'next': '/admin-pane/'})
        # This assert might be a bit fragile
        assert response.status_code == 302, "Couldn't log in admin user"

    def test_user_creation(self):
        self.login_admin()
        response = self.client.post('/admin-pane/auth/user/add/',
                {'username': self.TEST_USER, 'password1': 'test', 'password2': 'test', '_save': 'Save'})
        self.assertEqual(response.status_code, 302, 'Should redirect to User List page')
        self.assertTrue(DjangoUser.objects.filter(username=self.TEST_USER).exists(), 'Should create Django User')
        self.assertTrue(User.objects.filter(user__username=self.TEST_USER).exists(), 'Should create User Profile for user')

class CredentialTests(unittest.TestCase):
    def setUp(self):
        self.django_user = DjangoUser.objects.create(username=six.u('győzike'))
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
        self.assertEqual(decrypted, {six.u('cert') : 'cheese', six.u('password'):'wombles', six.u('key'):'it'})
        # logging in must encrypt the credential, and also shove a copy of the 
        # decrypted and then protected credential into the cache
        self.credential.get_credential_access().clear_cache()
        self.credential.on_login(self.django_user.username, 'pass')
        self.assertEqual(self.credential.security_state, Credential.ENCRYPTED)
        decrypted = self.credential.get_credential_access().get()
        self.assertEqual(decrypted, {six.u('cert') : 'cheese', six.u('password'):'wombles', six.u('key'):'it'})
        # and a final login, with the credentials encrypted in the db already
        self.assertEqual(self.credential.security_state, Credential.ENCRYPTED)
        self.credential.get_credential_access().clear_cache()
        self.credential.on_login(self.django_user.username, 'pass')
        decrypted = self.credential.get_credential_access().get()
        self.assertEqual(decrypted, {six.u('cert') : 'cheese', six.u('password'):'wombles', six.u('key'):'it'})        

    def test_cache_keyname_replaces_unicode_character(self):
        access = self.credential.get_credential_access()
        self.assertTrue('\\xc3\\x85\\xc2\\x91' in access.keyname, access.keyname)

    def test_cache(self):
        access = self.credential.get_credential_access()
        self.assertTrue(access.in_cache)
        self.assertEqual(access.get(), {six.u('cert') : 'cheese', six.u('password'):'wombles', six.u('key'):'it'})

class WsMenuTest(unittest.TestCase):
    def setUp(self):
        self.tool = None
        self.client = Client()
        cache.clear()
        self.login_fe('admin')

    def tearDown(self):
        if self.tool:
            ToolSet.objects.get(name='test').delete()
            Tool.objects.get(name='new-tool').delete()

    def test_menu_is_returned(self):
        response = self.client.get('/ws/menu/')
        self.assertEqual(response.status_code, 200, 'Should be able to get menu')
        menu = json.loads(response.content)['menu']
        self.assertEqual(len(menu['toolsets']), 1, 'Should have 1 toolset')
        toolset = menu['toolsets'][0]
        self.assertEqual(toolset['name'], 'all_tools', "Toolset should be 'all_tools'")
        tools = toolset['toolgroups'][0]['tools']
        self.assertEqual(len(tools), 1, "Should have 1 tool (fileselector)")
        self.assertEqual(tools[0]['name'], 'fileselector')

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
        self.assertTrue('new-tool' in tool_names, 'Should return new tool')

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
        tool = Tool.objects.create(
            name='new-tool', display_name='new_tool',
            backend=null_backend, fs_backend=null_backend)
        test_tset = ToolSet.objects.create(name='test')
        admin = User.objects.get(name='admin')
        test_tset.users.add(admin)
        select_data = ToolGroup.objects.get(name='select data')
        select_data.toolgrouping_set.create(tool_set=test_tset, tool=tool)
        return tool

    def login_fe(self, user, password=None):
        if password is None:
            password = user
        response = self.client.post('/login',
                {'username': user, 'password': password})
        assert response.status_code == 302, "Couldn't log in to FE"


class TestPytag(unittest.TestCase):
    def test_pytag(self):
        from django.template import Template, Context
        import yabiadmin.yabi.templatetags.pytag  # force registration of custom tag
        class Thing:
            def some_method(self, s, n):
                return "some result %s %d" % (s, n)

        obj = Thing()
        t = Template('{% load pytag %}HELLO{% py         obj.some_method(   "xyz",   100) %}GOODbye')
        c = Context({"obj": obj})
        result = t._render(c)
        self.assertEquals(result, six.u("HELLOsome result xyz 100GOODbye"))



class TestImportTag(unittest.TestCase):
    def test_importtag_populates_context(self):
        from django.template import Template, Context
        import yabiadmin.yabi.templatetags.importtag # register import tag
        import yabiadmin.yabi.templatetags.pytag     # register py tag
        # We use py tag also to illustrate usage of import
        import types
        m = types.ModuleType("foobar", "a test module")
        m.__dict__.update({"greet": lambda s: "Hello %s" % s})
        t = Template("{% load importtag %}{% load pytag %}start{% import foobar %}{% py foobar.greet('Fred Bloggs')%}finish")
        c = Context({"n": 100})  # Nb. no foobar module
        import sys
        sys.modules['foobar'] = m
        result = t._render(c)
        self.assertTrue('foobar' in c.dicts[-1] and result == six.u("startHello Fred Bloggsfinish"))

class TestOrderByCustomFilter(unittest.TestCase):
    def test_order_by_filter_generator(self):
        from yabiadmin.yabi.models import FileExtension  # could be anything

        from django.template import Template, Context

        exe_file = FileExtension.objects.create(pattern="zzzz")
        blah_file = FileExtension.objects.create(pattern="mmmm")
        jpg_file = FileExtension.objects.create(pattern="aaaa")

        all_extensions = FileExtension.objects.all()  # a generator


        test_template = """
        {% load order_by %}
        {% for fe in all_extensions|order_by:"pattern" %}
          {{fe.pattern}}
        {% endfor %}
        """

        context = Context({"all_extensions": all_extensions})
        result = Template(test_template).render(context)
        # template contains other extensions so we just locate the ones we created and ensure they're in the order in
        # the template we expect.
        index_of_aaaa = result.find("aaaa")
        index_of_mmmm = result.find('mmmm')
        index_of_zzzz = result.find('zzzz')
        self.assertTrue(index_of_zzzz > index_of_mmmm > index_of_aaaa, "order by failed")







