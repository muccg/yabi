import unittest

from model_mommy import mommy

from yabi.yabi.models import ParameterSwitchUse
from yabi.yabiengine import models as m
from yabi.yabiengine.commandlinetemplate import CommandTemplate, SwitchFilename, make_fname


class SwitchFilenameWithExtensionTest(unittest.TestCase):

    def setUp(self):
        self.switch = SwitchFilename(template=make_fname, extension='bls')

    def test_when_no_extension_adds_extension(self):
        self.switch.set('test')
        self.assertEquals('test.bls', '%s' % self.switch)

    def test_when_one_extension_changes_extension(self):
        self.switch.set('test.txt')
        self.assertEquals('test.bls', '%s' % self.switch)

    def test_when_2_extensions_changes_last_extension(self):
        self.switch.set('test.fa.txt')
        self.assertEquals('test.fa.bls', '%s' % self.switch)


class SwitchFilenameWithoutExtensionTest(unittest.TestCase):

    def setUp(self):
        self.switch = SwitchFilename(template=make_fname)

    def test_when_no_extension_doesnot_add_extension(self):
        self.switch.set('test')
        self.assertEquals('test', '%s' % self.switch)

    def test_doesnot_change_extension(self):
        self.switch.set('test.txt')
        self.assertEquals('test.txt', '%s' % self.switch)


class CommandLineTemplateTest(unittest.TestCase):

    def setUp(self):
        demo_user = m.User.objects.get(name='demo')
        workflow = mommy.make('Workflow', user=demo_user)
        self.job = mommy.make('Job', workflow=workflow, order=0)
        self.td = mommy.make('ToolDesc', name='my-tool')
        self.tool = mommy.make('Tool', desc=self.td, path='tool.sh')
        combined_with_equals = ParameterSwitchUse.objects.get(display_text='combined with equals')
        value_only = ParameterSwitchUse.objects.get(display_text='valueOnly')
        mommy.make('ToolParameter', tool=self.td, switch="-arg1", switch_use=combined_with_equals, rank=2)
        mommy.make('ToolParameter', tool=self.td, switch="-arg2", switch_use=value_only, rank=1)
        mommy.make('ToolParameter', tool=self.td, switch="-arg3", switch_use=value_only, file_assignment='batch')

        self.template = CommandTemplate()
        self.job_1_dict = {
            "jobId": 1,
            "toolName": "my-tool",
            "toolId": self.tool.id,
            "parameterList": {"parameter": []}}

    def tearDown(self):
        self.job.workflow.delete()
        self.td.delete()

    def job_dict_with_params(self, *params):
        import copy
        d = copy.copy(self.job_1_dict)
        if params:
            d['parameterList']['parameter'] = params
        return d

    def render_command(self, job, job_dict, uri_conversion=None):
        self.template.setup(job, job_dict)
        self.template.parse_parameter_description()

        if uri_conversion is not None:
            self.template.set_uri_conversion(uri_conversion)

        return self.template.render()

    def test_no_params(self):
        job_dict = self.job_1_dict

        command = self.render_command(self.job, job_dict)

        self.assertEquals("tool.sh", command)

    def test_param_combined_with_equals(self):
        job_dict = self.job_dict_with_params({
            'switchName': '-arg1',
            'valid': True,
            'value': ['value']})

        command = self.render_command(self.job, job_dict)

        self.assertEquals('tool.sh -arg1=value', command)

    def test_param_value_only(self):
        job_dict = self.job_dict_with_params({
            'switchName': '-arg2',
            'valid': True,
            'value': ['a value']})

        command = self.render_command(self.job, job_dict)

        self.assertEquals("tool.sh 'a value'", command)

    def test_rank_respected(self):
        job_dict = self.job_dict_with_params({
            'switchName': '-arg1',
            'valid': True,
            'value': ['value']},
            {
                'switchName': '-arg2',
                'valid': True,
                'value': ['other value']})

        command = self.render_command(self.job, job_dict)

        self.assertEquals("tool.sh 'other value' -arg1=value", command)

    def test_direct_file_reference(self):
        job_dict = self.job_dict_with_params({
            'switchName': '-arg3',
            'valid': True,
            'value': [{
                'path': ['some', 'path'],
                'root': 'sftp://demo@localhost:22/',
                'type': 'file',
                'filename': 'a file.txt'}]})

        command = self.render_command(self.job, job_dict, uri_conversion='/tools/workdir/input/%(filename)s')

        self.assertEquals("tool.sh '/tools/workdir/input/a file.txt'", command)

        # TODO Assert file will be staged in?
        # for f in self.template.other_files():
