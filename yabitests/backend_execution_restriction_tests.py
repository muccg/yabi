import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, YABI_FE
from fixture_helpers import admin
from request_test_base import RequestTestWithAdmin, TEST_USER
import os
import time
import sys
import json

def workflow(name="unnamed",toolname="hostname",number=5):
    wf = {
        'name':name,
        'tags':[],
        'jobs':[]
        }
        
    for job in range(number):
        wf['jobs'].append({
            "toolName":toolname,
            "jobId":job+1,
            "valid":True,
            "parameterList":{'parameter':[]}
        })
    
    return wf

class BackendRateLimitTest(RequestTestWithAdmin):
    
    def setUp(self):
        RequestTestWithAdmin.setUp(self)
        #admin.modify_backend("localex","localhost",tasks_per_user=CONCURRENT)
        admin.create_tool("hostname", display_name="hostname", path="hostname")
        admin.add_tool_to_all_tools("hostname")

    def tearDown(self):
        from yabiadmin.yabi import models
        models.Tool.objects.get(name='hostname').delete()
        RequestTestWithAdmin.tearDown(self)

    def change_backend_concurrent(self, concurrent):
        #login as admin
        import requests
        
        r = self.adminsession.post( YABI_FE+"/ws/modify_backend/name/localex/localhost", data={ 'tasks_per_user':concurrent } )
        self.assertTrue(r.status_code==200, "could not set the tasks_per_user on the backend localex://localhost. remote returned: %d"%r.status_code)

    def count_running(self,workflow_url):
        r = self.session.get( workflow_url )
        self.assertTrue(r.status_code==200, "Checking status of workflow failed")
        
        data = json.loads(r.text)
        status = data['status']
        
        # all the task statuses
        statuses = [job['status'] for job in data['json']['jobs']] 
        
        # count the occurances of tasks that aren't pending, ready, complete or error (and are thus running)
        return [X not in ['pending','ready','complete','error'] for X in statuses ].count(True), status
        
    def run_concurrent_backend(self, number, concurrent):
        import requests
          
        self.change_backend_concurrent(concurrent)
        our_workflow = workflow(number=number)
        
        r = self.session.post( YABI_FE+"/ws/workflows/submit", data = {'username':TEST_USER,'workflowjson':json.dumps(our_workflow)} )
        self.assertTrue(r.status_code==200, "Could not submit workflow")
        
        # lets get our workflow
        result = json.loads(r.text)
        jid = result['id']
        
        workflow_url = YABI_FE+"/ws/workflows/get/%d"%jid
        
        status = ""
        while status != "complete" and status!="error":
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            self.assertTrue(runs<=concurrent)
            
        self.change_backend_concurrent(None)
            
    def test_throttled_single_backend(self):
        return self.run_concurrent_backend(5,1)
        
    def test_throttled_multi_backend(self):
        return self.run_concurrent_backend(10,3)
        
    def test_throttled_large_backend(self):
        return self.run_concurrent_backend(20,10)
    
    def __test_stop_start_backend_limiting_on_the_fly(self):
        import requests
          
        self.change_backend_concurrent(1)               # 1 job at a time
        our_workflow = workflow(number=40)                     # 20 total in workflow
        
        r = self.session.post( YABI_FE+"/ws/workflows/submit", data = {'username':TEST_USER,'workflowjson':json.dumps(our_workflow)} )
        self.assertTrue(r.status_code==200, "Could not submit workflow")
        
        # lets get our workflow
        result = json.loads(r.text)
        jid = result['id']
        
        workflow_url = YABI_FE+"/ws/workflows/get/%d"%jid
        
        # wait for one task to start
        runs = 0
        while runs!=1:
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            self.assertTrue(runs==0 or runs==1, "wrong number of jobs running concurrently")
            self.assertTrue(status!="complete" and status!="error", "incorrect status on workflow")
        
        # now one is running. lets stop it
        self.change_backend_concurrent(0)
        
        while runs!=0:
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            self.assertTrue(runs==0 or runs==1, "wrong number of jobs running concurrently")
            self.assertTrue(status!="complete" and status!="error", "incorrect status on workflow")
        
        # now its finished and we've got zero running. lets make sure one doesnt start up for a little while
        for checks in range(30):
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            self.assertTrue(runs==0, "wrong number of jobs running concurrently")
            self.assertTrue(status!="complete" and status!="error", "incorrect status on workflow")
            
        # now lets fire 1 up again
        self.change_backend_concurrent(1)
        
        while runs!=1:
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            self.assertTrue(runs==0 or runs==1, "wrong number of jobs running concurrently")
            self.assertTrue(status!="complete" and status!="error", "incorrect status on workflow")
            
        # now one is running, lets up the limit and watch 3 fire up
        self.change_backend_concurrent(3)
        
        while runs!=3:
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            self.assertTrue(runs>=1 or runs<=3, "wrong number of jobs running concurrently")
            self.assertTrue(status!="complete" and status!="error", "incorrect status on workflow")
        
        # now three are running lets stop them all
        self.change_backend_concurrent(0)
        
        while runs!=0:
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            self.assertTrue(runs>=0 or runs<=3, "wrong number of jobs running concurrently")
            self.assertTrue(status!="complete" and status!="error", "incorrect status on workflow")
        
        # now they're stopped. lets make sure none start for a while
        for checks in range(30):
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            self.assertTrue(runs==0, "wrong number of jobs running concurrently")
            self.assertTrue(status!="complete" and status!="error", "incorrect status on workflow")
            
        # none have started. lets finish these jobs off
        self.change_backend_concurrent(20)
    
        # wait for the whole workflow to finish
        status = ""
        while status != "complete" and status!="error":
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            self.assertTrue(runs<=20)
            
        self.change_backend_concurrent(None)
