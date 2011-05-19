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
# Goes through all the users and reports if some Workflows are found in 
# Postgres but not in SQLLite.
# To run start up a shell_plus and call into report():
#
# yabiadmin $ fab manage:shell_plus
# shell> from scripts import report_missing_sqllite_data as r
# shell> r.report() 
#

from yabi.models import User
from yabistoreapp import db

from django.db import connection


# entry point
def report():
    users = get_all_users()
    for user in users:
        print '-' * 20
        print user
        try:
            sql_ids = get_sqllite_ids(user)
            psql_ids = get_psql_ids(user)
            missing = filter(lambda x: x not in sql_ids, psql_ids)
            if missing:
                print "The following Workflows are missing from SQLite:"
                print ",".join([str(id) for id in missing])
            else:
                print "No data missing"
        except Exception, e:
            print e

def get_all_users():
    return [u.name for u in User.objects.all()]

def get_sqllite_ids(user):
    sqll_wfls = db.get_workflows(user)
    return filter(lambda x: x is not None, [s.get("id", None) for s in sqll_wfls])
 
def get_psql_ids(user):
    cur = connection.cursor()
    cur.execute("SELECT w.id FROM yabiengine_workflow w JOIN yabi_user u ON u.id=user_id " +
                "WHERE u.name = %s", (user,))
    return [r[0] for r in cur] 
