# -*- coding: utf-8 -*-

import json
import sys
from django.utils import unittest as unittest
from model_mommy import mommy
from yabi.yabi.ws_frontend_views import munge_name
from yabi.yabi.models import User, Backend, BackendCredential, Credential, Tool, ToolDesc, ToolSet, ToolGroup
from yabi.test_utils import USER, ADMIN_USER, DjangoTestClientTestCase
from django.contrib.auth.models import User as DjangoUser
from django.core.cache import cache


class AddNewToolMixin(object):

    def add_new_tool(self):
        admin = User.objects.get(name=ADMIN_USER)
        backend = Backend.objects.get(name='Local Execution')
        fs_backend = Backend.objects.get(name='nullbackend')
        self.cred = Credential.objects.create(description="test cred", user=admin, username="admin")
        self.bc = BackendCredential.objects.create(backend=backend, credential=self.cred)
        desc = ToolDesc.objects.create(name='new-tool')
        tool = Tool.objects.create(desc=desc, backend=backend, fs_backend=fs_backend)
        self.test_tset = ToolSet.objects.create(name='test')
        self.test_tset.users.add(admin)
        select_data = ToolGroup.objects.get(name='select data')
        select_data.toolgrouping_set.create(tool_set=self.test_tset, tool=tool)

        def cleanup():
            tool.delete()
            desc.delete()
            self.test_tset.delete()
            self.cred.delete()
            self.bc.delete()
        self.addCleanup(cleanup)

        return tool


class WsMenuTest(DjangoTestClientTestCase, AddNewToolMixin):
    def setUp(self):
        DjangoTestClientTestCase.setUp(self)
        self.tool = None
        cache.clear()
        self.login_fe(ADMIN_USER)

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


class TestLsWithExtraBackendCredentials(DjangoTestClientTestCase):
    def setUp(self):
        DjangoTestClientTestCase.setUp(self)
        # Preloaded by quickstart
        self.PRELOADED_BC = BackendCredential.objects.get(pk=2)
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
            [[self.PRELOADED_BC.homedir_uri, 0, False],
             [expected_homedir_uri, 0, False]],
            listing[USER]['directories'])


class GetWorkflowTests(DjangoTestClientTestCase):
    def setUp(self):
        DjangoTestClientTestCase.setUp(self)
        self.user = User.objects.get(name=USER)
        self.workflow = mommy.make('Workflow', name='A test workflow', user=self.user)
        self.login_fe(ADMIN_USER)

    def tearDown(self):
        self.workflow.delete()

    def get_workflow(self, pk):
        return self.client.get('/ws/workflows/get/%s' % pk)

    def test_get_of_inexisting_workflow_should_be_404(self):
        response = self.get_workflow(1001)
        self.assertEqual(response.status_code, 404)

    def test_get_of_existing_workflow_by_owner_should_be_ok(self):
        self.login_fe(USER)
        response = self.get_workflow(self.workflow.pk)
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp['id'], self.workflow.pk)

    def test_get_of_existing_workflow_by_other_user_should_be_forbidden(self):
        response = self.get_workflow(self.workflow.pk)
        self.assertEqual(response.status_code, 403)

    def test_get_of_existing_shared_workflow_by_other_user_should_be_ok(self):
        self.workflow.share()
        response = self.get_workflow(self.workflow.pk)
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp['id'], self.workflow.pk)
        self.assertEqual(resp['shared'], True)


class ShareWorkflowTests(DjangoTestClientTestCase):
    def setUp(self):
        DjangoTestClientTestCase.setUp(self)
        self.user = User.objects.get(name=USER)
        other_user = DjangoUser.objects.create(username='otheruser')
        other_user.set_password('otheruser')
        other_user.save()
        self.other_user = other_user.user
        self.workflow = mommy.make('Workflow', name='A test workflow', user=self.user)
        self.login_fe(ADMIN_USER)

    def tearDown(self):
        self.workflow.delete()
        self.other_user.user.delete()
        self.other_user.delete()

    def share_workflow(self, pk):
        return self.client.post('/ws/workflows/share', {'id': pk})

    def test_share_of_inexisting_workflow_should_be_404(self):
        response = self.share_workflow(1001)
        self.assertEqual(response.status_code, 404)

    def test_share_of_existing_workflow_by_owner_should_be_ok(self):
        self.login_fe(USER)
        response = self.share_workflow(self.workflow.pk)
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp['status'], 'success')
        self.assertEqual(resp['data'], 'shared')

    def test_share_of_existing_workflow_by_admin_should_be_ok(self):
        response = self.share_workflow(self.workflow.pk)
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp['status'], 'success')
        self.assertEqual(resp['data'], 'shared')

    def test_share_of_existing_workflow_by_other_user_should_be_forbidden(self):
        self.login_fe('otheruser')
        response = self.share_workflow(self.workflow.pk)
        self.assertEqual(response.status_code, 403)


class GetToolTest(DjangoTestClientTestCase, AddNewToolMixin):
    def setUp(self):
        DjangoTestClientTestCase.setUp(self)
        self.tool = self.add_new_tool()
        cache.clear()
        self.login_fe(ADMIN_USER)

    def test_not_found_is_returned_for_unexisting_tool(self):
        response = self.client.get('/ws/tool/%s' % sys.maxsize)
        self.assertEqual(response.status_code, 404, 'Should return not found')

    def test_tool_is_returned(self):
        response = self.client.get('/ws/tool/%s' % self.tool.pk)
        self.assertEqual(response.status_code, 200, 'Should be able to get tool')
        tool = json.loads(response.content)['tool']
        self.assertEqual(tool['display_name'], 'new-tool')

    def test_forbidden_is_returned_if_no_backend_credential_for_user(self):
        # Changing the credential to belong to the other user
        demo = User.objects.get(name='demo')
        self.cred.user = demo
        self.cred.save()
        response = self.client.get('/ws/tool/%s' % self.tool.pk)
        self.assertEqual(response.status_code, 403, 'Should not be able to get tool')
 
    def test_forbidden_is_returned_if_not_in_users_toolset(self):
        # Remove the user from the toolset
        admin = User.objects.get(name=ADMIN_USER)
        self.test_tset.users.remove(admin)
        response = self.client.get('/ws/tool/%s' % self.tool.pk)
        self.assertEqual(response.status_code, 403, 'Should not be able to get tool')
        self.test_tset.users.add(admin)
