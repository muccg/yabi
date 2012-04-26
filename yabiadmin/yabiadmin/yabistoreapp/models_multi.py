### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
from django.db import models
from django.db import load_backend
from django.utils import simplejson as json
from django.conf import settings
from django.db.models import sql, options
from django.db.models.query import QuerySet
from django.db.models.sql import BaseQuery
from django.db.transaction import savepoint_state
from django.core import signals
from yabiadmin.yabistoreapp.json_util import *

import logging
logger = logging.getLogger(__name__)

options.DEFAULT_NAMES += ('db_name',)

try:
    import thread
except ImportError:
    import dummy_thread as thread

_connections = {}

# Register an event that closes the database connections
# when a Django request is finished. This stops the "Database Locked" errors
def close_connection(**kwargs):
    global _connections
    for connection in _connections.itervalues():
        connection.close()
    _connections = {}
signals.request_finished.connect(close_connection, dispatch_uid="close_connection")

class MultiDBManager(models.Manager):
    @staticmethod
    def get_db_connection(model):
        print "MODEL",model
        db_name = getattr(model._meta, 'db_name', None)   # get a parameter on the models meta that refers to the database it is stored in. This can be used for sharding
        print "DB_NAME",db_name
        if not db_name is None:
            if callable(db_name):
                # callable returns the actual settings
                settings_dict = db_name()
                db_name = settings_dict['DB_NAME']
            else:
                settings_dict = settings.DATABASES[db_name] if hasattr(settings,'DATABASES') else model.DATABASES[db_name]
            if not _connections.has_key(db_name):         # cached connections
                print "=>",settings_dict
                backend = load_backend(settings_dict['DATABASE_ENGINE'])
                wrapper = backend.DatabaseWrapper(MultiDBManager._get_settings(settings_dict))
                wrapper._cursor()
                _connections[db_name] = wrapper
            return _connections[db_name]
        else:
            from django.db import connection
            print "=> DEFAULT"
            return connection
        
    @staticmethod
    def _get_settings(settings_dict):
        return {
            'DATABASE_HOST': settings_dict.get('DATABASE_HOST'),
            'DATABASE_NAME': settings_dict.get('DATABASE_NAME'),
            'DATABASE_OPTIONS': settings_dict.get('DATABASE_OPTIONS') or settings.DATABASE_OPTIONS,
            'DATABASE_PASSWORD': settings_dict.get('DATABASE_PASSWORD'),
            'DATABASE_PORT': settings_dict.get('DATABASE_PORT'),
            'DATABASE_USER': settings_dict.get('DATABASE_USER'),
            'TIME_ZONE': settings.TIME_ZONE,
        }  

    def get_query_set(self):
        connection = MultiDBManager.get_db_connection(self.model)
        if connection.features.uses_custom_query_class:
            Query = connection.ops.query_class(BaseQuery)
        else:
            Query = BaseQuery
        qs = QuerySet(self.model, Query(self.model, connection))
        return qs
    
    def _insert(self, values, return_id=False, raw_values=False):
        query = sql.InsertQuery(self.model, self.get_db_connection(self.model))
        query.insert_values(values, raw_values)
        ret = query.execute_sql(return_id)
        query.connection._commit()
        thread_ident = thread.get_ident()
        if thread_ident in savepoint_state:
            del savepoint_state[thread_ident]
        return ret



class MultiDBModel(models.Model):
    # when we are a base class our manager is an instance of MultiDBManager.
    _base_manager = MultiDBManager()

    class Meta:
        abstract = True

    #@classmethod
    #def init_database(cls, username):

        #import os
        #import shutil

        #user_storage_path = settings.STORAGE_DIR + username + '/'
        #user_db_path = user_storage_path + 'yabistore.db'

        #if not os.path.exists(user_storage_path):
            #try:
                #os.mkdir(user_storage_path)
            #except OSError, e:
                #logger.critical('Unable to create storage directory for user: %s' %  e)
                #raise

        ## copy a template in place if no db
        #if not os.path.exists(user_db_path):
            #logger.debug('Copying template database to %s' % user_db_path)
            #try:
                #shutil.copyfile(settings.DATABASE_TEMPLATE, user_db_path)

            #except (shutil.Error, IOError), e:
                #logger.critical('Unable to copy template database to user directory: %s' % e)
                #raise

        #cls.database["DATABASE_NAME"] = user_db_path

def current_db():
    return {
            'DB_NAME': 'testing',
            'DATABASE_ENGINE' : 'sqlite3',
            'DATABASE_NAME' : '/tmp/test.sqlite3',
        }

class Tag(MultiDBModel):

    class Meta:
        db_name = current_db

    value = models.CharField(max_length=255)

##    def __init__(self, *args, **kwargs):
        
##        if 'username' in kwargs:
##            (user_storage_path, user_db_path) = user_db_exists(kwargs['username'])
##            print "path is " + user_db_path
##            self.database["DATABASE_NAME"] = user_db_path
##            del(kwargs["username"])
##        else:
##            self.database["DATABASE_NAME"] = self.default_dbname
            
##        super(Workflow, self).__init__(*args, **kwargs)


    #MultiDBManager = type('MultiDBManager', (MultiDBManager,), {'database':MultiDBModel.database})
    
    
    #MultiDBManager.database = MultiDBModel.database
    objects =  MultiDBManager()
    objects.use_for_related_fields = True
    
    def __unicode__(self):
        return self.value

        

class Workflow(MultiDBModel):
    class Meta:
        db_name = current_db

    name = models.CharField(max_length=255)
    json = models.TextField(blank=True)
    last_modified_on = models.DateTimeField(null=True, auto_now=True, editable=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    status = models.TextField(max_length=64, blank=True)

    tags = models.ManyToManyField(Tag, null=True, blank=True, through="WorkflowTag")

    #MultiDBManager.database = MultiDBModel.database
    objects =  MultiDBManager()
    objects.use_for_related_fields = True

class WorkflowTag(MultiDBModel):
    class Meta:
        db_name = current_db
        
    workflow = models.ForeignKey(Workflow)
    tag = models.ForeignKey(Tag)
    





##    def __init__(self, *args, **kwargs):
        
##        if 'username' in kwargs:
##            (user_storage_path, user_db_path) = user_db_exists(kwargs['username'])
##            print "path is " + user_db_path
##            self.database["DATABASE_NAME"] = user_db_path
##            del(kwargs["username"])
##        else:
##            self.database["DATABASE_NAME"] = self.default_dbname
            
##        super(Workflow, self).__init__(*args, **kwargs)

    
    def __unicode__(self):
        return self.name

    def workflow_dict(self):
        """
        Returns a dictionary with the data from this object with out the json.
        This is so we can spit them out as json without having the json field
        encoded twice
        """
        workflow_dict = self.__dict__
        del workflow_dict['json']
        return workflow_dict
