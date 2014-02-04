from django.utils import unittest as unittest
from django.test.client import Client

from datetime import datetime, timedelta

from yabiadmin.test_utils import override_settings

from yabiadmin.yabiengine import enginemodels as emodels
from yabiadmin.yabi.models import User, Backend
from yabiadmin.yabiengine import models
from yabiadmin.yabiengine.commandlinetemplate import SwitchFilename, make_fname
from yabiadmin.constants import *

from urlparse import urlparse
from django.utils.http import urlencode
import hmac
from django.conf import settings


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

