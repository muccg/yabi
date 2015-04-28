from model_mommy import mommy
from yabi.yabi.models import User
from yabi.test_utils import USER, ADMIN_USER, DjangoTestClientTestCase


class ReuseTest(DjangoTestClientTestCase):
    def setUp(self):
        DjangoTestClientTestCase.setUp(self)
        self.user = User.objects.get(name=USER)
        self.workflow = mommy.make('Workflow', name='A test workflow', user=self.user)
        self.login_fe(ADMIN_USER)

    def tearDown(self):
        self.workflow.delete()

    def test_reuse_of_inexisting_workflow_should_be_404(self):
        response = self.client.get('/design/reuse/1001')
        self.assertEqual(response.status_code, 404)

    def test_reuse_of_existing_workflow_by_owner_should_be_ok(self):
        self.login_fe(USER)
        response = self.client.get('/design/reuse/%s' % self.workflow.pk)
        self.assertEqual(response.status_code, 200)

    def test_reuse_of_existing_workflow_by_other_user_should_be_forbidden(self):
        response = self.client.get('/design/reuse/%s' % self.workflow.pk)
        self.assertEqual(response.status_code, 403)
