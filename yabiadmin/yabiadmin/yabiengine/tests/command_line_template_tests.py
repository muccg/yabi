from django.utils import unittest as unittest

from yabiadmin.yabiengine import models
from yabiadmin.yabiengine.commandlinetemplate import CommandTemplate, SwitchFilename, make_fname


class SwitchFilenameWithExtensionTest(unittest.TestCase):

    def setUp(self):
        self.switch = SwitchFilename(template=make_fname, extension='bls')

    def test_when_no_extension_adds_extension(self):
        self.switch.set('test')
        self.assertEquals('"test.bls"', '%s' % self.switch)

    def test_when_one_extension_changes_extension(self):
        self.switch.set('test.txt')
        self.assertEquals('"test.bls"', '%s' % self.switch)

    def test_when_2_extensions_changes_last_extension(self):
        self.switch.set('test.fa.txt')
        self.assertEquals('"test.fa.bls"', '%s' % self.switch)


class SwitchFilenameWithoutExtensionTest(unittest.TestCase):

    def setUp(self):
        self.switch = SwitchFilename(template=make_fname)

    def test_when_no_extension_doesnot_add_extension(self):
        self.switch.set('test')
        self.assertEquals('"test"', '%s' % self.switch)

    def test_doesnot_change_extension(self):
        self.switch.set('test.txt')
        self.assertEquals('"test.txt"', '%s' % self.switch)


from yabiadmin.yabi.models import User, ParameterSwitchUse
from yabiadmin.yabiengine import models as m

from  model_mommy import mommy

class CommandLineTemplateTest(unittest.TestCase):

    def setUp(self):
        demo_user = m.User.objects.get(name='demo')
        workflow = mommy.make('Workflow', user=demo_user)
        self.job = mommy.make('Job', workflow=workflow, order=0)
        self.tool = mommy.make('Tool', name='my-tool', path='tool.sh')
        combined_with_equals = ParameterSwitchUse.objects.get(display_text='combined with equals')
        value_only = ParameterSwitchUse.objects.get(display_text='valueOnly')
        self.tool_param = mommy.make('ToolParameter', tool=self.tool, switch="-arg1", switch_use=combined_with_equals)
        self.tool_param = mommy.make('ToolParameter', tool=self.tool, switch="-arg2", switch_use=value_only)

        self.template = CommandTemplate()

    def tearDown(self):
        self.job.workflow.delete()
        self.tool.delete()

    def test_no_params(self):
        job_dict = {
            "jobId": 1,
            "toolName": "my-tool",
            "parameterList": {"parameter": []}}
        self.template.setup(self.job, job_dict)
        self.template.parse_parameter_description()

        command = self.template.render()

        self.assertEquals("tool.sh", command)

    def test_param_combined_with_equals(self):
        job_dict = {
            "jobId": 1,
            "toolName": "my-tool",
            "parameterList": {"parameter": [{
                    'switchName': '-arg1',
                    'valid': True,
                    'value': ['value'] }]}}
        self.template.setup(self.job, job_dict)
        self.template.parse_parameter_description()

        command = self.template.render()

        self.assertEquals('tool.sh -arg1="value"', command)

    def test_param_value_only(self):
        job_dict = {
            "jobId": 1,
            "toolName": "my-tool",
            "parameterList": {"parameter": [{
                    'switchName': '-arg2',
                    'valid': True,
                    'value': ['value'] }]}}
        self.template.setup(self.job, job_dict)
        self.template.parse_parameter_description()

        command = self.template.render()

        self.assertEquals('tool.sh "value"', command)


