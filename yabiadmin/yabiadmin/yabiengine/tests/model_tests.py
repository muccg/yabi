from django.utils import unittest as unittest

from  model_mommy import mommy

from yabiadmin.yabi.models import User, ParameterSwitchUse
from yabiadmin.yabiengine import models as m
from yabiadmin.yabiengine.commandlinetemplate import CommandTemplate, SwitchFilename, make_fname


def create_workflow_with_job_and_2_tasks(obj):
    demo_user = m.User.objects.get(name='demo')
    obj.workflow = mommy.make('Workflow', user=demo_user)
    obj.job = mommy.make('Job', workflow=obj.workflow, order=0)
    obj.task = mommy.make('Task', job=obj.job)
    obj.second_task = mommy.make('Task', job=obj.job)
    obj.tool = mommy.make('Tool', name='my-tool', path='tool.sh')

def delete_models(*args):
    for model in args:
        model.delete()

class TaskRetryingTest(unittest.TestCase):

    def setUp(self):
        create_workflow_with_job_and_2_tasks(self)

    def tearDown(self):
        delete_models(self.workflow, self.tool)

    def test_not_retrying_by_default(self):
        self.assertFalse(self.task.is_retrying)
        self.assertFalse(self.second_task.is_retrying)
        self.assertFalse(self.job.is_retrying)
        self.assertFalse(self.workflow.is_retrying)


class TaskRetryingOneTaskMarkedAsRetryingTest(unittest.TestCase):

    def setUp(self):
        create_workflow_with_job_and_2_tasks(self)

        # We mark the second task as retrying, with an error msg
        from yabiadmin.backend.celerytasks import mark_task_as_retrying
        self.second_task.mark_task_as_retrying("Big error")

    def tearDown(self):
        delete_models(self.workflow, self.tool)

    def test_task_is_retrying(self):
        second_task_reloaded = m.Task.objects.get(pk=self.second_task.pk)

        self.assertTrue(second_task_reloaded.is_retrying)

    def test_task_error_msg_is_set(self):
        second_task_reloaded = m.Task.objects.get(pk=self.second_task.pk)

        self.assertEquals("Big error", second_task_reloaded.error_msg)

    def test_job_and_workflow_are_retrying(self):
        self.assertTrue(self.job.is_retrying)
        self.assertTrue(self.workflow.is_retrying)

    def test_task_not_retrying_after_task_recovered_from_error(self):
        self.second_task.recovered_from_error()

        second_task_reloaded = m.Task.objects.get(pk=self.second_task.pk)

        self.assertFalse(second_task_reloaded.is_retrying)

    def test_task_error_msg_cleared_after_task_recovered_from_error(self):
        self.second_task.recovered_from_error()

        second_task_reloaded = m.Task.objects.get(pk=self.second_task.pk)

        self.assertTrue(second_task_reloaded.error_msg is None)

    def test_job_and_workflow_not_retrying_after_task_recovered_from_error(self):
        self.second_task.recovered_from_error()

        self.assertFalse(self.job.is_retrying)
        self.assertFalse(self.workflow.is_retrying)

