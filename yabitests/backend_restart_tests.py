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

    def stop_backend(self):
        os.system("cd $YABI_DIR/yabibe/yabibe && virt_yabibe/bin/fab killbackend")
    
    def start_backend(self):
        os.system("cd $YABI_DIR/yabibe/yabibe && virt_yabibe/bin/fab backend:bg")

    def test_single_task_restart(self):
        # run backend tasks one at a time so we can restart the backend during execution
        self.change_backend_concurrent(1) 
        our_workflow = workflow(number=5)
        
        r = self.session.post( YABI_FE+"/ws/workflows/submit", data = {'username':TEST_USER,'workflowjson':json.dumps(our_workflow)} )
        self.assertTrue(r.status_code==200, "Could not submit workflow")
        
        # lets get our workflow
        result = json.loads(r.text)
        jid = result['id']
        
        workflow_url = YABI_FE+"/ws/workflows/get/%d"%jid
        
        time.sleep(15)
        self.stop_backend()
        time.sleep(15)
        self.start_backend()
            
        self.change_backend_concurrent(None)