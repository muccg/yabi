# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.core.management import call_command
from django.db.utils import DatabaseError
from south.db import db

class Migration(SchemaMigration):

    def forwards(self, orm):
        try:
            call_command("createcachetable", "yabi_cache")
        except DatabaseError, e:
            print "Cache table already exists."

    def backwards(self, orm):
        db.delete_table('yabi_cache', cascade=True)


    complete_apps = ['yabi']
