from django.utils import unittest as unittest
from django.test.client import Client

from datetime import datetime, timedelta

from yabiadmin.test_utils import override_settings

from yabiadmin.yabiengine import enginemodels as emodels
from yabiadmin.yabi.models import User, Backend
from yabiadmin.yabiengine import models
from yabiengine.commandlinetemplate import SwitchFilename, make_fname
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
        self.assertTrue('No more tasks' in response.content)

class TaskViewWithTasksTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        user = User.objects.get(name='demo') 
        wfl = emodels.EngineWorkflow.objects.create(user=user)
        fs_backend = Backend.objects.get(name='Local Filesystem')
        self.job = emodels.EngineJob.objects.create(workflow=wfl, order=2, start_time=datetime.now(), 
            fs_backend= 'localfs://localhost/')
        self.task = emodels.EngineTask.objects.create(job=self.job, tasktag= 'test_tasktag')
    
    @override_settings(TASKTAG='test_tasktag')
    def test_task_no_ready_tasks(self):
        self.task.status = 'pending'
        response = self.client.get('/engine/task', {'tasktag': 'test_tasktag'})
        self.assertEqual(response.status_code, 404)
        self.assertTrue('No more tasks' in response.content)

    def minutes(self, m):
        return timedelta(minutes=m)

    def test_status_normal_order(self):
        now = datetime.now()
        self.task.status_pending = now - self.minutes(2) 
        self.task.status_ready = now - self.minutes(1) 
        self.task.status_requested = now 
        self.assertEqual(self.task.status, 'requested')

    def test_status_normal_order_some_missing(self):
        now = datetime.now()
        self.task.status_pending = now - self.minutes(10) 
        self.task.status_complete = now 
        self.assertEqual(self.task.status, 'complete')

    def test_status_out_of_order(self):
        now = datetime.now()
        self.task.status_complete = now - self.minutes(10) 
        self.task.status_pending = now 
        self.assertEqual(self.task.status, 'complete')


class CommandLineTemplateTest(unittest.TestCase):

    def test_switch_filename(self):
        s = SwitchFilename(template=make_fname, extension='bls')
        s.set('test.txt')
        self.assertEquals('"test.bls"', '%s' % s)
        s.set('test.bls') 
        self.assertEquals('"test.bls"', '%s' % s)
        s.set('test.fa.txt')
        self.assertEquals('"test.fa.bls"', '%s' % s)        
        s = SwitchFilename(template=make_fname)
        s.set('test.txt')
        self.assertEquals('"test.txt"', '%s' % s)
        s.set('test')
        self.assertEquals('"test"', '%s' % s)        
