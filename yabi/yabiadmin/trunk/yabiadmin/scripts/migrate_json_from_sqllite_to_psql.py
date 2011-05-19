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
# Migrates the json and the Tags of a Workflow from SQLLite to Postgres.
# SQLLite files should be moved out of the way after the migration finished,
# the new DB files will be created automatically.
# To run start up a shell_plus and call into migrate():
#
# yabiadmin $ fab manage:shell_plus
# shell> from scripts import migrate_json_from_sqllite_to_psql as m
# 
# To make a simulation only do (now True by default):
#
# shell> m.DontAct = True
#
# shell> m.migrate(USERNAME) 
#
# or to migrate all users call without args:
#
# shell> m.migrate() 
#
# If you want to do the migration for real set back DontAct to False first
#
# shell> m.DontAct = False

from yabi.models import User
from yabistoreapp import db
from yabiengine.enginemodels import EngineWorkflow
from collections import namedtuple
from django.db import transaction
import json


class MissingDataError(StandardError):
    def __init__(self, msg, ids):
        StandardError.__init__(self, msg)
        self.ids = ids

MigrationError = namedtuple('MigrationError', 'user msg details')

# Set to True to allow making DB changes
DontAct = True

# entry point
def migrate(*users):
    if not users:
        users = get_all_users()
    failed = []
    succeeded = []
    for user in users:
        try:
            migrate_user(user, DontAct)
        except MissingDataError, e:
            failed.append(MigrationError(user, str(e), 
                "The following workflows don't have SQLLite data:\n %s" % 
                    ','.join([str(x) for x in e.ids])))
            continue
        except Exception, e:
            failed.append(MigrationError(user, str(e), 'No idea'))
            continue

        succeeded.append(user)
    if succeeded:
        print 'The following users have their data migrated:'
        for user in succeeded:
            print user
        print 'You should backup their history DBs now:'
        print 'Something like:'
        for user in succeeded:
            histfile = db.user_fs_home(user) + '/history.sqlite3'
            backup = db.user_fs_home(user) + '/history.sqlite3.migrated'
            print 'mv %s %s' % (histfile, backup)
    if failed:
        print 'For the following users the migration has FAILED:'
        for mig_err in failed:
            print mig_err.user
            print 'Error: ' + mig_err.msg
            print 'Details/Resolution: ' + mig_err.details
            print '-' * 20

def get_all_users():
    return [u.name for u in User.objects.all()]


@transaction.commit_on_success
def migrate_user(user, dont_act):
    sqll_wfls = db.get_workflows(user)
    sqll_wfl_ids = filter(lambda x: x is not None, [s.get("id", None) for s in sqll_wfls])
    missing = EngineWorkflow.objects.exclude(pk__in=sqll_wfl_ids).filter(user__name=user)
    if missing:
        raise MissingDataError('User %s has missing sqllite data' % user, 
                [wfl.id for wfl in missing])
    psql_wfls = EngineWorkflow.objects.filter(json=None)
    for from_wfl in sqll_wfls:
        if 'id' not in from_wfl: continue
        try:
            to_wfl = EngineWorkflow.objects.get(pk=from_wfl['id'])
            if to_wfl.json is None:
                if not dont_act:
                    to_wfl.json = json.dumps(from_wfl['json'])
                    to_wfl.change_tags(from_wfl['tags'])
                    to_wfl.save()
        except EngineWorkflow.DoesNotExist:
            print 'The following SQLite Workflow has no Postgres correspondent: ' + str(from_wfl['id'])
            pass

