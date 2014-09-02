from django.utils import unittest as unittest
from model_mommy import mommy
from yabiadmin.yabiengine import models as m


def create_workflow_with_job_and_2_tasks(testcase):
    demo_user = m.User.objects.get(name='demo')
    testcase.workflow = mommy.make('Workflow', user=demo_user)
    testcase.job = mommy.make('Job', workflow=testcase.workflow, order=0)
    testcase.task = mommy.make('Task', job=testcase.job)
    testcase.second_task = mommy.make('Task', job=testcase.job)
    testcase.tooldesc = mommy.make('ToolDesc', name='my-tool')
    testcase.tool = mommy.make('Tool', desc=testcase.tooldesc, path='tool.sh')

    def cleanup():
        testcase.workflow.delete()
        testcase.tooldesc.delete()
    testcase.addCleanup(cleanup)


class TaskRetryingTest(unittest.TestCase):

    def setUp(self):
        create_workflow_with_job_and_2_tasks(self)

    def test_not_retrying_by_default(self):
        self.assertFalse(self.task.is_retrying)
        self.assertFalse(self.second_task.is_retrying)
        self.assertFalse(self.job.is_retrying)
        self.assertFalse(self.workflow.is_retrying)


class TaskRetryingOneTaskMarkedAsRetryingTest(unittest.TestCase):

    def setUp(self):
        create_workflow_with_job_and_2_tasks(self)

        # We mark the second task as retrying, with an error msg
        self.second_task.mark_task_as_retrying("Big error")

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
        self.second_task.finished_retrying()

        second_task_reloaded = m.Task.objects.get(pk=self.second_task.pk)

        self.assertFalse(second_task_reloaded.is_retrying)

    def test_task_error_msg_cleared_after_task_recovered_from_error(self):
        self.second_task.finished_retrying()

        second_task_reloaded = m.Task.objects.get(pk=self.second_task.pk)

        self.assertTrue(second_task_reloaded.error_msg is None)

    def test_job_and_workflow_not_retrying_after_task_recovered_from_error(self):
        self.second_task.finished_retrying()

        self.assertFalse(self.job.is_retrying)
        self.assertFalse(self.workflow.is_retrying)
