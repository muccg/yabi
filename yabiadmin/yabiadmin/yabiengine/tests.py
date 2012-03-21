from django.utils import unittest as unittest
from django.test.client import Client

from datetime import datetime

from yabiadmin.test_utils import override_settings

from yabiadmin.yabiengine import enginemodels as emodels
from yabiadmin.constants import *

class TaskViewNoTasksTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_task_no_tasktag(self):
        response = self.client.get('/engine/task')
        self.assertEqual(response.status_code, 500)
        self.assertTrue('No tasktag' in response.content)

    @override_settings(TASKTAG='test_tasktag')
    def test_task_incorrect_tasktag(self):
        response = self.client.get('/engine/task', {'tasktag': 'NOT MATCHING'})
        self.assertEqual(response.status_code, 500)
        self.assertTrue('Tasktag incorrect' in response.content)

    @override_settings(TASKTAG='test_tasktag')
    def test_task_no_ready_tasks(self):
        response = self.client.get('/engine/task', {'tasktag': 'test_tasktag'})
        self.assertEqual(response.status_code, 404)
        self.assertTrue('Object not found' in response.content)

class TaskViewWithTasksTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        wfl = emodels.EngineWorkflow.objects.create()
        self.job = emodels.EngineJob.objects.create(workflow=wfl, order=1, start_time=datetime.now())
        task = emodels.EngineTask.objects.create(job=self.job, status=STATUS_PENDING, tasktag= 'test_tasktag')
        
    @override_settings(TASKTAG='test_tasktag')
    def xtest_task_no_ready_tasks(self):
        response = self.client.get('/engine/task', {'tasktag': 'test_tasktag'})
        self.assertEqual(response.status_code, 404)
        self.assertTrue('Object not found' in response.content)

    @override_settings(TASKTAG='test_tasktag')
    def xtest_task_one_ready_task(self):
        task = emodels.EngineTask.objects.create(job=self.job, status=STATUS_READY, tasktag='test_tasktag')
        response = self.client.get('/engine/task', {'tasktag': 'test_tasktag'})
        self.assertEqual(response.status_code, 404)
        self.assertTrue('Object not found' in response.content)




