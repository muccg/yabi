# -*- coding: utf-8 -*-

from django.utils import unittest as unittest
from django.test.client import Client
from model_mommy import mommy
from yabiadmin.yabi.ws_frontend_views import munge_name
from yabiadmin.yabi.models import User, Backend, Tool, ToolSet, ToolGroup
from django.core.cache import cache

from django.utils import simplejson as json


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
