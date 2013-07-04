import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, conf
from fixture_helpers import admin
from request_test_base import RequestTestWithAdmin
import os
import time
import sys
import json
import requests
from yabiadmin.yabi import models


def workflow(name="unnamed", toolname="sleep", number=5):
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
            "parameterList":{'parameter':[{
                "valid": True, 
                "value": [
                  "2"
                ], 
                "switchName": "seconds"
            }]}
        })
    
    return wf


class BackendRateLimitTest(RequestTestWithAdmin):
    
    def setUp(self):
        RequestTestWithAdmin.setUp(self)
        admin.create_tool_sleep()

    def tearDown(self):
        RequestTestWithAdmin.tearDown(self)
        admin.remove_tool_from_all_tools('sleep')
        tool = models.Tool.objects.get(name='sleep')
        tool.delete()

    def change_backend_concurrent(self, concurrent):
        sys.stderr.write('Throttling to {0}\n'.format(concurrent))

        r = self.adminsession.post( conf.yabiurl+"/ws/modify_backend/name/localex/localhost", data={ 'tasks_per_user':concurrent } )
        self.assertTrue(r.status_code==200, "could not set the tasks_per_user on the backend localex://localhost. remote returned: %d"%r.status_code)

    def get_workflow_json(self, workflow_url):
        r = self.session.get( workflow_url )
        self.assertTrue(r.status_code==200, "Checking status of workflow failed")
        return json.loads(r.text)

    def count_running(self, workflow_url):
        rval = 0

        r = self.session.get(workflow_url)
        self.assertTrue(r.status_code==200, "Checking status of workflow failed")

        data = json.loads(r.text)
        status = data['status']

        for job in data['json']['jobs']:
            if 'status' not in job or job['status'] in ['ready','complete','error']:
                continue
            rval += 1

        return rval, status

    def wait_for_workflow_to_finish(self, workflow_url, concurrent):
        status = ""
        while status != "complete" and status!="error":
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            sys.stderr.write('{0}'.format(runs))
            self.assertTrue(runs <= concurrent)
        sys.stderr.write('\n')

    def wait_for_tasks_to_finish(self, workflow_url, concurrent):
        running = True
        while running:
            time.sleep(1)
            runs, status = self.count_running(workflow_url)
            sys.stderr.write('{0}'.format(runs))
            self.assertTrue(runs <= concurrent)

            data = self.get_workflow_json(workflow_url)
            running = False
            for job in data['json']['jobs']:
                if 'status' in job and job['status'] not in ['complete', 'error']:
                    running = True
                    continue
        sys.stderr.write('\n')

    def submit_workflow(self, number, concurrent):
        self.change_backend_concurrent(concurrent)
        our_workflow = workflow(number=number)
        
        r = self.session.post(conf.yabiurl + "/ws/workflows/submit", data = {'username':conf.yabiusername,'workflowjson':json.dumps(our_workflow)})
        self.assertTrue(r.status_code==200, "Could not submit workflow")
        
        # lets get our workflow
        result = json.loads(r.text)
        jid = result['id']
        return conf.yabiurl + "/ws/workflows/get/%d" % jid
    
    def get_backend_task_debug(self):
        r = requests.get( conf.yabibeurl + "debug" )
        self.assertTrue(r.status_code==200, "tried to access backend debug and got remote error: %d"%r.status_code)
        dat = json.loads(r.text)
        return dat

    def stop_backend(self):
        os.system(conf.stopyabibe)
    
    def start_backend(self):
        os.system(conf.startyabibe)
            
    def test_throttled_backend(self):
        concurrent = 10
        workflow_url = self.submit_workflow(10, concurrent)
        self.wait_for_workflow_to_finish(workflow_url, concurrent)
        self.change_backend_concurrent("None")

        count, status = self.count_running(workflow_url)
        assert(count == 0)

    def test_single_workflow_restart(self):
        concurrent = 20
        workflow_url = self.submit_workflow(20, concurrent)
        
        # catch one of the tasks running
        while True:
            time.sleep(1)
            count, status = self.count_running(workflow_url)
            sys.stderr.write('{0}'.format(count))
            if count != 0:
                break
        sys.stderr.write('\n')

        #self.stop_backend()
#        self.change_backend_concurrent(10) 
        #self.start_backend()
#        
#        # wait for the count to get above 5
#        while True:
#            time.sleep(1)
#            count, status = self.count_running(workflow_url)
#            sys.stderr.write('{0}'.format(count))
#            if count > 5:
#                break
#        sys.stderr.write('\n')
#            
#        self.stop_backend()
#        self.start_backend()
#        
#        # make sure there are at least 5 restarted
#        dat = self.get_backend_task_debug()
#        self.assertTrue(len(dat)>=5, "Less than 5 jobs restarted")
#
#        concurrent = 10
#        self.change_backend_concurrent(concurrent)
        self.wait_for_tasks_to_finish(workflow_url, concurrent)
        self.change_backend_concurrent(None)

        count, status = self.count_running(workflow_url)
        assert(count == 0)
