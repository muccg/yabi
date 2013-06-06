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

class BackendRestartTest(RequestTestWithAdmin):
    
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
    
    def count_running(self, workflow_url):
        rval = 0

        r = self.session.get(workflow_url)
        self.assertTrue(r.status_code==200, "Checking status of workflow failed")
        
        data = json.loads(r.text)
        status = data['status']
        
        for job in data['json']['jobs']: 
            if 'status' in job and job['status'] in ['ready','complete','error']:
                continue
            rval += 1
        
        return rval
    
    def return_running(self,workflow_url):
        r = self.session.get( workflow_url )
        self.assertTrue(r.status_code==200, "Checking status of workflow failed")
        
        return json.loads(r.text)
        
    def get_backend_task_debug(self):
        import requests
        
        r = requests.get( conf.yabibeurl + "debug" )
        self.assertTrue(r.status_code==200, "tried to access backend debug and got remote error: %d"%r.status_code)
        
        dat = json.loads(r.text)
        return dat

    def stop_backend(self):
        os.system(conf.stopyabibe)
        os.system(conf.yabistatus)
    
    def start_backend(self):
        os.system(conf.startyabibe)

    def test_single_task_restart(self):
        # run backend tasks one at a time so we can restart the backend during execution
        self.change_backend_concurrent(2) 
        our_workflow = workflow(number=30)
        
        r = self.session.post( conf.yabiurl+"/ws/workflows/submit", data = {'username':conf.yabiusername,'workflowjson':json.dumps(our_workflow)} )
        self.assertTrue(r.status_code==200, "Could not submit workflow")
 
        print "posted workflow"
        
        # lets get our workflow
        result = json.loads(r.text)
        jid = result['id']
        workflow_url = conf.yabiurl+"/ws/workflows/get/%d"%jid
        
        # catch one of the tasks running
        count = self.count_running(workflow_url)
        while count == 0:
            time.sleep(0.2)
            count = self.count_running(workflow_url)
            sys.stderr.write('{0}'.format(count))
        
        self.stop_backend()
        self.change_backend_concurrent(10) 
        self.start_backend()
        
        # wait for the count to get above 5
        count = self.count_running(workflow_url)
        while count <= 5:
            time.sleep(0.5)
            count = self.count_running(workflow_url)
            sys.stderr.write('{0}'.format(count))
            
        self.stop_backend()
        self.start_backend()
        
        # make sure there are at least 5 restarted
        dat = self.get_backend_task_debug()
        
        self.assertTrue(len(dat)>=5, "Less than 5 jobs restarted")
        
        # wait for all the jobs to finish now
        concurrent = 10
        self.change_backend_concurrent(concurrent)
        
        running = True
        while running:
            time.sleep(1)
            runs = self.count_running(workflow_url)
            sys.stderr.write('{0}'.format(runs))
            self.assertTrue(runs <= concurrent)

            # there is a bug where one task stays as 'requested'. if everything is 'complete' except for one.
            data = self.return_running(workflow_url)
            running = False
            for job in data['json']['jobs']:
                if job['status'] not in ['complete', 'error']:
                    running = True
                        
        self.change_backend_concurrent(None)
