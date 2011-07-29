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
from yabife import settings
from yabife.ldapclient import LDAPClient

def get_all_users():
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    filter = "(objectclass=person)"
    result = ldapclient.search(settings.AUTH_LDAP_USER_BASE, filter)

    return dict(result)

def get_yabi_userids():
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    filter = "(cn=%s)" % settings.AUTH_LDAP_USER_GROUP
    result = ldapclient.search(settings.AUTH_LDAP_GROUP_BASE, filter, [ 'uniqueMember'] )
    return set(result[0][1]['uniqueMember'])
      
def get_userdn_of(username):
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    userfilter = "(&(objectclass=person) (uid=%s))" % username
    result = ldapclient.search(settings.AUTH_LDAP_USER_BASE, userfilter, ['dn'])
    if result and len(result) == 1:
        return result[0][0]

def can_bind_as(userdn, password):
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    try:
        if ldapclient.bind_as(userdn, password):
            return True
    finally:
        ldapclient.unbind()

def is_user_member_of(userdn, groupname):
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    groupfilter = '(&(objectClass=groupofuniquenames)(uniqueMember=%s)(cn=%s))' % (userdn, groupname)
    result = ldapclient.search(settings.AUTH_LDAP_GROUP_BASE, groupfilter, ['cn'])
    return len(result) == 1

