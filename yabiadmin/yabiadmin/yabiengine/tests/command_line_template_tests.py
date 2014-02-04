from django.utils import unittest as unittest

from yabiadmin.yabiengine import models
from yabiadmin.yabiengine.commandlinetemplate import SwitchFilename, make_fname


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

