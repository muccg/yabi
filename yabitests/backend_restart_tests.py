import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, YABI_FE, YABI_BE, YABI_DIR
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

class BackendRestartTest(RequestTestWithAdmin):
    @classmethod
    def setUpAdmin(self):
        #admin.modify_backend("localex","localhost",tasks_per_user=CONCURRENT)
        admin.create_tool(name="hostname", display_name="hostname", path="hostname")
        admin.add_tool_to_all_tools("hostname")

    @classmethod
    def tearDownAdmin(self):
        from yabiadmin.yabi import models
        models.Tool.objects.get(name='hostname').delete()

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
    
    def return_running(self,workflow_url):
        r = self.session.get( workflow_url )
        self.assertTrue(r.status_code==200, "Checking status of workflow failed")
        
        return json.loads(r.text)
        
    def get_backend_task_debug(self):
        import requests
        
        r = requests.get( YABI_BE+"/debug" )
        self.assertTrue(r.status_code==200, "tried to access backend debug and got remote error: %d"%r.status_code)
        
        dat = json.loads(r.text)
        return dat

    def stop_backend(self):
        os.system("cd %s/yabibe/yabibe && . virt_yabibe/bin/activate && fab killbackend"%YABI_DIR)
    
    def start_backend(self):
        os.system("cd %s/yabibe/yabibe && . virt_yabibe/bin/activate && fab backend:bg"%YABI_DIR)

    def test_single_task_restart(self):
        # run backend tasks one at a time so we can restart the backend during execution
        self.change_backend_concurrent(1) 
        our_workflow = workflow(number=30)
        
        r = self.session.post( YABI_FE+"/ws/workflows/submit", data = {'username':TEST_USER,'workflowjson':json.dumps(our_workflow)} )
        self.assertTrue(r.status_code==200, "Could not submit workflow")
        
        # lets get our workflow
        result = json.loads(r.text)
        jid = result['id']
        
        workflow_url = YABI_FE+"/ws/workflows/get/%d"%jid
        
        #sys.stderr.write("counting... %s\n"%(self.count_running(workflow_url)[0]))
        
        # wait for one of the tasks to actually start up.
        while self.count_running(workflow_url)[0]<1:
            time.sleep(1)
        
        self.stop_backend()
        self.change_backend_concurrent(10) 
        time.sleep(10)
        self.start_backend()
        
        # wait for the count to get above 5
        while self.count_running(workflow_url)[0]<=5:
            sys.stderr.write(".")
            time.sleep(1)
            
        self.stop_backend()
        time.sleep(10)
        self.start_backend()
        
        # make sure there are at least 5 restarted
        dat = self.get_backend_task_debug()
        
        self.assertTrue(len(dat)>=5, "Less than 5 jobs restarted")
        #pprint = json.dumps(dat, sort_keys=True, indent=4)
        #sys.stderr.write(pprint+"\n")
        
        # wait for all the jobs to finish now
        concurrent=10
        self.change_backend_concurrent(concurrent)
        
        status = ""
        while status != "complete" and status!="error":
            sys.stderr.write(".")
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            self.assertTrue(runs<=concurrent)
            
            # there is a bug where one task stays as 'requested'. if everything is 'complete' except for one.
            data = self.return_running(workflow_url)
            statuses = [job['status'] for job in data['json']['jobs']] 
            #statuses = [job for job in data['json']['jobs']] 
            #sys.stderr.write("\n%s\n"%(str(statuses)))
            if len([X for X in statuses if X!='complete' and X!='ready'])==0:
                self.assertTrue(statuses.count('ready')==0, "possible frozen job in ready/requested state. workflow: %d"%jid)
                        
            
        self.change_backend_concurrent(None)