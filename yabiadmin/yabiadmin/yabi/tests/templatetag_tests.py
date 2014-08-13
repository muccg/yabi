# -*- coding: utf-8 -*-

import six
from django.utils import unittest as unittest


class TestPytag(unittest.TestCase):
    def test_pytag(self):
        from django.template import Template, Context
        # force registration of custom tag
        import yabiadmin.yabi.templatetags.pytag  # NOQA

        class Thing:
            def some_method(self, s, n):
                return "some result %s %d" % (s, n)

        obj = Thing()
        t = Template('{% load pytag %}HELLO{% py         obj.some_method(   "xyz",   100) %}GOODbye')
        c = Context({"obj": obj})
        result = t._render(c)
        self.assertEquals(result, six.u("HELLOsome result xyz 100GOODbye"))


class TestImportTag(unittest.TestCase):
    def test_importtag_populates_context(self):
        from django.template import Template, Context
        # register import and py tags
        import yabiadmin.yabi.templatetags.importtag
        import yabiadmin.yabi.templatetags.pytag      # NOQA
        # We use py tag also to illustrate usage of import
        import types
        m = types.ModuleType("foobar", "a test module")
        m.__dict__.update({"greet": lambda s: "Hello %s" % s})
        t = Template("{% load importtag %}{% load pytag %}start{% import foobar %}{% py foobar.greet('Fred Bloggs')%}finish")
        c = Context({"n": 100})  # Nb. no foobar module
        import sys
        sys.modules['foobar'] = m
        result = t._render(c)
        self.assertTrue('foobar' in c.dicts[-1] and result == six.u("startHello Fred Bloggsfinish"))


from yabiadmin.yabi.models import FileExtension  # could be anything


class TestOrderByCustomFilter(unittest.TestCase):
    def setUp(self):
        self.extensions = [
            FileExtension.objects.create(pattern="zzzz"),
            FileExtension.objects.create(pattern="mmmm"),
            FileExtension.objects.create(pattern="aaaa"),
        ]

    def tearDown(self):
        for ext in self.extensions:
            ext.delete()

    def test_order_by_filter_generator(self):

        from django.template import Template, Context

        all_extensions = FileExtension.objects.all()  # a generator

        test_template = """
        {% load order_by %}
        {% for fe in all_extensions|order_by:"pattern" %}
          {{fe.pattern}}
        {% endfor %}
        """

        context = Context({"all_extensions": all_extensions})
        result = Template(test_template).render(context)
        # template contains other extensions so we just locate the ones we created and ensure they're in the order in
        # the template we expect.
        index_of_aaaa = result.find("aaaa")
        index_of_mmmm = result.find('mmmm')
        index_of_zzzz = result.find('zzzz')
        self.assertTrue(index_of_zzzz > index_of_mmmm > index_of_aaaa, "order by failed")
