# -*- coding: utf-8 -*-

from django.utils import unittest as unittest
from django.test.client import Client
from model_mommy import mommy
from yabiadmin.yabi.ws_frontend_views import munge_name
from yabiadmin.yabi.models import User, Backend, BackendCredential, Credential, Tool, ToolSet, ToolGroup
from django.core.cache import cache

from django.utils import simplejson as json


USER = 'demo'
ADMIN_USER = 'admin'


class WSTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.client = Client()

    def login_fe(self, user, password=None):
        if password is None:
            password = user
        response = self.client.post('/login', {
            'username': user, 'password': password})
        assert response.status_code == 302, "Couldn't log in to FE"


class WsMenuTest(WSTestCase):
    def setUp(self):
        WSTestCase.setUp(self)
        self.tool = None
        cache.clear()
        self.login_fe(ADMIN_USER)

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
        self.login_fe(USER)
        user_menu = self.client.get('/ws/menu')
        self.assertNotEqual(admin_menu.content, user_menu.content,
                            "Shouldn't get the same response from cache")

    def add_new_tool(self):
        null_backend = Backend.objects.get(name='nullbackend')
        tool = Tool.objects.create(
            name='new-tool', display_name='new_tool',
            backend=null_backend, fs_backend=null_backend)
        test_tset = ToolSet.objects.create(name='test')
        admin = User.objects.get(name=ADMIN_USER)
        test_tset.users.add(admin)
        select_data = ToolGroup.objects.get(name='select data')
        select_data.toolgrouping_set.create(tool_set=test_tset, tool=tool)
        return tool


class TestWorkflowNameMunging(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.get(name=USER)
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
        name = munge_name(self.user.workflow_set, 'does not exist yet')
        self.assertEquals('does not exist yet', name)

    def test_unmunged_unique_workflow_name(self):
        name = munge_name(self.user.workflow_set, 'Unmunged yet')
        self.assertEquals('Unmunged yet (1)', name)

    def test_already_munged_called_with_basename(self):
        name = munge_name(self.user.workflow_set, 'Munged')
        self.assertEquals('Munged (3)', name)

    def test_already_munged_called_with_munged_name(self):
        name = munge_name(self.user.workflow_set, 'Munged (1)')
        self.assertEquals('Munged (3)', name)


class TestLsWithExtraBackendCredentials(WSTestCase):
    def setUp(self):
        WSTestCase.setUp(self)
        # Preloaded by quickstart
        self.PRELOADED_BC = BackendCredential.objects.get(pk=3)
        self.setUpExtraBackendCredentials()
        self.login_fe(USER)
        self.maxDiff = None

    def setUpExtraBackendCredentials(self):
        # just use first preloaded Credential of USER
        credential = Credential.objects.filter(user__name=USER)[0]

        self.be = mommy.make('Backend', scheme='sftp', hostname='some.host.com', port=2222, path='/some/home/')
        self.dynbe = mommy.make('Backend', dynamic_backend=True)

        self.bc = mommy.make('BackendCredential', backend=self.be, credential=credential, homedir='someusername', visible=True)
        # Visible set to False, shouldn't show up
        self.invisible_bc = mommy.make('BackendCredential', backend=self.be, credential=credential, homedir='other_dir', visible=False)

        # Associated with Dynamic Backend, shouldn't show up
        self.dynbe_bc = mommy.make('BackendCredential', backend=self.dynbe, credential=credential, homedir='another_dir', visible=True)

    def tearDown(self):
        self.bc.delete()
        self.invisible_bc.delete()
        self.dynbe_bc.delete()

        self.be.delete()
        self.dynbe.delete()

    def test_ls_with_no_uri_returns_visible_backend_credentials(self):
        response = self.client.get('/ws/fs/ls')
        listing = json.loads(response.content)

        # BackendCredentials with Visible False should never show up
        # BackendCredentials associated with Dynamic Backends should never show up
        # The listing will have the preloaded BackendCredential and the only
        # BackendCredential we created with visible True and associated with a
        # non-dynamic backend
        expected_homedir_uri = 'sftp://%s@some.host.com:2222/some/home/someusername' % USER
        self.assertIn(USER, listing, 'Should be keyed by username')
        self.assertEquals(1, len(listing), 'Should be only one entry')
        self.assertEquals([], listing[USER]['files'], 'Should have empty files array')
        self.assertItemsEqual(
            [[self.PRELOADED_BC.homedir_uri, 0, ''],
             [expected_homedir_uri, 0, '']],
            listing[USER]['directories'])
