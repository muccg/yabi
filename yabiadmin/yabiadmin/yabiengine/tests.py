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


class CommandLineTemplateTest(unittest.TestCase):

    def test_switch_filename(self):
        s = SwitchFilename(template=make_fname, extension='bls')
        s.set('test.txt')
        self.assertEquals('"test.bls"', '%s' % s)
        s.set('test.bls')
        self.assertEquals('"test.bls"', '%s' % s)
        s.set('test.fa.txt')
        self.assertEquals('"test.fa.bls"', '%s' % s)
        s = SwitchFilename(template=make_fname)
        s.set('test.txt')
        self.assertEquals('"test.txt"', '%s' % s)
        s.set('test')
        self.assertEquals('"test"', '%s' % s)
