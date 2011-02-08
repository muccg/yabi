# Migrates the json and the Tags of a Workflow from SQLLite to Postgres.
# SQLLite files should be moved out of the way after the migration finished,
# the new DB files will be created automatically.
# To run start up a shell_plus and call into migrate():
#
# yabiadmin $ fab manage:shell_plus
# shell> from scripts import migrate_json_from_sqllite_to_psql as m
# shell> m.migrate(USERNAME) 
#

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

# entry point
def migrate(*users):
    if not users:
        users = get_all_users()
    failed = []
    succeeded = []
    for user in users:
        try:
            migrate_user(user)
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
def migrate_user(user):
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
                to_wfl.json = json.dumps(from_wfl['json'])
                to_wfl.change_tags(from_wfl['tags'])
                to_wfl.save()
        except EngineWorkflow.DoesNotExist:
            print 'MISSING: ' + str(from_wfl['id'])
            pass

