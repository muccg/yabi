import os
import sys
sys.path.append('home/lee/src/yabi/yabiadmin')
os.environ['DJANGO_SETTINGS_MODULE'] = 'yabiadmin.settings'
from yabiadmin.yabi.templatetags import pytag # force registration of custom tag
from django.test import TestCase
from django.template import Template, Context

class TestPytag(TestCase):
    def test_pytag(self):
        class Thing:
            def some_method(self, s):
                return "some result %s" % s

        obj = Thing()
        t = Template('<% py obj.some_method("xyz") %>')
        c = Context({"obj": obj})
        result = t._render(c)
        self.assertEquals(result, "some result xyz")
