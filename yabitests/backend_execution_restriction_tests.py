import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, conf
from fixture_helpers import admin
from request_test_base import RequestTestWithAdmin
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
        admin.add_tool_to_all_tools("hostname")

    def tearDown(self):
        RequestTestWithAdmin.tearDown(self)

    def change_backend_concurrent(self, concurrent):
        #login as admin
        import requests
        
        r = self.adminsession.post( conf.yabiurl+"/ws/modify_backend/name/localex/localhost", data={ 'tasks_per_user':concurrent } )
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
        
        r = self.session.post( conf.yabiurl+"/ws/workflows/submit", data = {'username':conf.yabiusername,'workflowjson':json.dumps(our_workflow)} )
        self.assertTrue(r.status_code==200, "Could not submit workflow")
        
        # lets get our workflow
        result = json.loads(r.text)
        jid = result['id']
        
        workflow_url = conf.yabiurl+"/ws/workflows/get/%d"%jid
        
        status = ""
        while status != "complete" and status!="error":
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            self.assertTrue(runs<=concurrent)
            
        self.change_backend_concurrent("None")
            
    def test_throttled_backend(self):
        return self.run_concurrent_backend(10,2)
    
