# -*- coding: utf-8 -*-

from django.utils import unittest as unittest
from django.test.client import Client
from django.contrib.auth.models import User as DjangoUser
from model_mommy import mommy
from yabiadmin.yabi.ws_frontend_views import munge_name
from yabiadmin.yabi.models import Credential, User, Backend, Tool, ToolSet, ToolGroup
from yabiadmin.yabi.forms import BackendForm
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
        self.assertTrue('\\xc3\\x85\\xc2\\x91' in access.keyname, access.keyname)

    def test_cache(self):
        access = self.credential.get_credential_access()
        self.assertTrue(access.in_cache)
        self.assertEqual(access.get(), {six.u('cert'): 'cheese', six.u('password'): 'wombles', six.u('key'): 'it'})


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
        response = self.client.post('/login', {
            'username': user, 'password': password})
        assert response.status_code == 302, "Couldn't log in to FE"


class TestPytag(unittest.TestCase):
    def test_pytag(self):
        from django.template import Template, Context
        # force registration of custom tag
        import yabiadmin.yabi.templatetags.pytag  # NOQA

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
        # register import and py tags
        import yabiadmin.yabi.templatetags.importtag
        import yabiadmin.yabi.templatetags.pytag      # NOQA
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


from yabiadmin.yabi.models import FileExtension  # could be anything


class TestOrderByCustomFilter(unittest.TestCase):
    def setUp(self):
        self.extensions = [
            FileExtension.objects.create(pattern="zzzz"),
            FileExtension.objects.create(pattern="mmmm"),
            FileExtension.objects.create(pattern="aaaa"),
        ]

    def tearDown(self):
        for ext in self.extensions:
            ext.delete()

    def test_order_by_filter_generator(self):

        from django.template import Template, Context

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


class TestWorkflowNameMunging(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.get(name='demo')
        self.workflow = mommy.make('Workflow', name='Unmunged yet', user=self.user)
        self.munged_workflows = [
            mommy.make('Workflow', name='Munged', user=self.user),
            mommy.make('Workflow', name='Munged (1)', user=self.user),
            mommy.make('Workflow', name='Munged (2)', user=self.user),
        ]

    def tearDown(self):
        self.workflow.delete()
        for w in self.munged_workflows:
            w.delete()

    def test_unique_name_does_not_get_munged(self):
        name = munge_name(self.user.name, 'does not exist yet')
        self.assertEquals('does not exist yet', name)

    def test_unmunged_unique_workflow_name(self):
        name = munge_name(self.user.name, 'Unmunged yet')
        self.assertEquals('Unmunged yet (1)', name)

    def test_already_munged_called_with_basename(self):
        name = munge_name(self.user.name, 'Munged')
        self.assertEquals('Munged (3)', name)

    def test_already_munged_called_with_munged_name(self):
        name = munge_name(self.user.name, 'Munged (1)')
        self.assertEquals('Munged (3)', name)


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
