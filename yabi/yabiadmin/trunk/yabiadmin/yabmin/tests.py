import unittest
from django.test import TestCase
from django.test.client import Client
from yabiadmin.yabmin.models import *
from yabiadmin.yabiengine.models import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.utils import simplejson as json

class TestYabmin(unittest.TestCase):
    #fixtures = ['test_data.json'] # this does not seem to work

    def setUp(self):

        # change authentication to backend on the fly
        # manual says don't do this, but we are only testing right?
        settings.AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
        settings.DEBUG = True
        settings.YABISTORE_SERVER = "127.0.0.1:8001"
        settings.YABISTORE_BASE = ""


        
        user, created = User.objects.get_or_create(name="testuser")
        if created:
            user.save()
        self.assertNotEqual(user, None)


    def tearDown(self):
        pass




    ########################################
    ## tool
    ########################################

    def testTool(self):

        # test existing tool
        c = Client()
        response = c.get('/ws/tool/blast.xe.ivec.org')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["tool"]["name"], "blast.xe.ivec.org")

    def testInvalidTool(self):
        # test non-existant to ensure we don't explode app
        c = Client()
        response = c.get('/ws/tool/testingtool_thisshouldnotexist')
        self.assertEqual(response.status_code, 404)




    ########################################
    ## menu
    ########################################

    def testMenu(self):

        # get menu for andrew
        c = Client()
        response = c.get('/ws/menu/andrew?yabiusername=andrew')
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        toolset = payload["menu"]["toolsets"][0]
        toolgroup = toolset["toolgroups"][0]
        tool = toolgroup["tools"][0]        

        self.assertEqual(toolset["name"], "dev")
        self.assertEqual(toolgroup["name"], "blast")
        self.assertEqual(tool["name"], "blast.xe.ivec.org")
        self.assertEqual(tool["displayName"], "blast")
        self.assertEqual(tool["outputExtensions"][0], "bls")
        self.assertEqual(tool["inputExtensions"][0], "fa")        


    def testInvalidMenu(self):
        # test non-existant user to ensure we don't explode app
        # menu is set up to return empty json structure but not
        # return 404 so it does not break front end
        c = Client()
        response = c.get('/ws/menu/testingtool_thisshouldnotexist?yabiusername=andrew')
        self.assertEqual(response.status_code, 403)


    def testMenuDifferentUser(self):
        """
        This test is designed to check that menu DOES NOT return another users
        menu items
        """
        # get menu for cwellington with yabiusername of andrew
        c = Client()
        response = c.get('/ws/menu/cwellington?yabiusername=andrew')
        self.assertEqual(response.status_code, 403)

    def testMenuButNoYabiusername(self):

        # get menu for andrew
        c = Client()
        response = c.get('/ws/menu/andrew')
        self.assertEqual(response.status_code, 403)




    ########################################
    ## credential
    ########################################

    def testCredential(self):

        # get credential for andrew
        c = Client()
        response = c.get('/ws/credential/gridftp/amacgregor/xe-ng2.ivec.org')
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertEqual(payload["username"], "amacgregor")
        self.assertEqual(payload["scheme"], "gridftp")


    def testInvalidCredential(self):
        c = Client()
        response = c.get('/ws/credential/gridftp/testing_this_should_fail/xe-ng2.ivec.org')
        self.assertEqual(response.status_code, 404)


    def testCredentialDetailCert(self):
        c = Client()
        response = c.get('/ws/credential/gridftp/amacgregor/xe-ng2.ivec.org/cert')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("-----BEGIN CERTIFICATE-----" in response.content)


    def testCredentialDetailKey(self):
        c = Client()
        response = c.get('/ws/credential/gridftp/amacgregor/xe-ng2.ivec.org/key')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("-----BEGIN RSA PRIVATE KEY-----" in response.content)


    def testCredentialDetailUsername(self):
        c = Client()
        response = c.get('/ws/credential/gridftp/amacgregor/xe-ng2.ivec.org/username')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("amacgregor" in response.content)




    ########################################
    ## submitWorkflow
    ########################################

    def testSubmitWorkflow(self):
        c = Client()

        workflowjson = '{"name":"unittest","jobs":[{"toolName":"fileselector","jobId":1,"valid":true,"parameterList":{"parameter":[{"switchName":"files","valid":true,"value":["1003_5915.fa"]}]}},{"toolName":"fastasplitter","jobId":2,"valid":true,"parameterList":{"parameter":[{"switchName":"-i","valid":true,"value":["file://localhost.localdomain/input/1003_5915.fa"]}]}},{"toolName":"blast.xe.ivec.org","jobId":3,"valid":true,"parameterList":{"parameter":[{"switchName":"-p","valid":true,"value":["blastn"]},{"switchName":"-d","valid":true,"value":["nt"]},{"switchName":"-i","valid":true,"value":[{"type":"job","jobId":2}]}]}},{"toolName":"blasttophits","jobId":4,"valid":true,"parameterList":{"parameter":[{"switchName":"inputFiles","valid":true,"value":[{"type":"job","jobId":3}]},{"switchName":"hitCount","valid":true,"value":["10"]}]}}]}'

        response = c.post('/ws/submitworkflow',
                          {'username':'andrew',
                           'workflowjson': workflowjson
                           })

        self.assertEqual(response.status_code, 200)

        wf = Workflow.objects.get(name='unittest')
        self.assertTrue(wf.json, workflowjson)
        self.assertTrue(wf.user.name, 'andrew')

        jobs = Job.objects.filter(workflow=wf).order_by('order')
        self.assertTrue(len(jobs),3)

        j1 = jobs[0]
        self.assertTrue(j1.exec_backend,'globus://xe-ng2.ivec.org/scratch')        
        self.assertTrue(j1.fs_backend,'gridftp://xe-ng2.ivec.org/scratch')        
        self.assertTrue(j1.stageout,'gridftp://andrew@xe-ng2.ivec.org/bi01/amacgregor/1/1/')        
        self.assertTrue(j1.status,'pending')
        self.assertTrue(j1.command,'/scratch/bi01/amacgregor/bin/ccg-fastasplitter -i %')
        self.assertTrue(j1.commandparams,"[u'file://localhost.localdomain/input/1003_5915.fa']")
        self.assertTrue(j1.input_filetype_extensions,"[u'fa', u'fasta', u'faa', u'fna']")

        j2 = jobs[1]
        self.assertTrue(j2.exec_backend,'globus://xe-ng2.ivec.org/scratch')        
        self.assertTrue(j2.fs_backend,'gridftp://xe-ng2.ivec.org/scratch')        
        self.assertTrue(j2.stageout,'gridftp://andrew@xe-ng2.ivec.org/bi01/amacgregor/1/2/')
        self.assertTrue(j2.status,'pending')
        self.assertTrue(j2.command,'blastall -i %')
        self.assertTrue(j2.commandparams,"[u'yabi://localhost.localdomain/1/1/']")
        self.assertTrue(j2.input_filetype_extensions,"[u'fa', u'faa', u'gb', u'fna']")


        j3 = jobs[2]
        self.assertTrue(j3.exec_backend,'local://localhost.localdomain:8000')
        self.assertTrue(j3.fs_backend,'file://localhost.localdomain:8000')
        self.assertTrue(j3.stageout,'file://andrew@localhost.localdomain:8003/andrew/1/3/')
        self.assertTrue(j3.status,'pending')
        self.assertTrue(j3.command,'/usr/local/bin/ccg-blastparser %')
        self.assertTrue(j3.commandparams,"[u'yabi://localhost.localdomain/1/2/']")
        self.assertTrue(j3.input_filetype_extensions,"[u'bls']")



    ########################################
    ## ls
    ########################################
    def testLsInvalidUserInUri(self):

        c = Client()
        response = c.get('/ws/fs/list?uri=gripftp://cwellington@xe-ng2.ivec.org/scratch/bio1/andrew/workspace/')
        self.assertEqual(response.status_code, 403) # this should be forbidden

