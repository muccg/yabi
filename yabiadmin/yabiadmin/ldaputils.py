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
import traceback, hashlib, base64
from ldap import LDAPError, MOD_REPLACE
from yabiadmin import settings
from yabiadmin.ldapclient import LDAPClient
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

class LdapUser:
    def __init__(self, uid, dn, full_name):
        self.uid = uid
        self.dn = dn
        self.full_name = full_name


class LDAPUserDoesNotExist(ObjectDoesNotExist):
    pass


def get_all_users():
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    filter = "(objectclass=person)"
    result = ldapclient.search(settings.AUTH_LDAP_USER_BASE, filter)

    return dict(result)

def get_yabi_userids():
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    filter = "(cn=%s)" % settings.AUTH_LDAP_GROUP
    result = ldapclient.search(settings.AUTH_LDAP_GROUP_BASE, filter, [ 'uniqueMember'] )
    return set(result[0][1]['uniqueMember'])
      
def get_userdn_of(username):
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    userfilter = "(&(objectclass=person) (uid=%s))" % username
    result = ldapclient.search(settings.AUTH_LDAP_USER_BASE, userfilter, ['dn'])
    if result and len(result) == 1:
        return result[0][0]
    else:
        raise LDAPUserDoesNotExist

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

def format(dn, ldap_user):
    return LdapUser(ldap_user['uid'][0], dn, ldap_user['cn'][0])

def set_ldap_password(user, current_password, new_password, bind_userdn=None, bind_password=None):

    assert current_password, "No currentPassword was supplied."
    assert new_password, "No newPassword was supplied."

    try:
        userdn = get_userdn_of(user.username)
        client = LDAPClient(settings.AUTH_LDAP_SERVER)

        if bind_userdn and bind_password:
            client.bind_as(bind_userdn, bind_password)
        else:
            client.bind_as(userdn, current_password)

        md5 = hashlib.md5(new_password).digest()
        modlist = (
            (MOD_REPLACE, "userPassword", "{MD5}%s" % (base64.encodestring(md5).strip(), )),
        )
        client.modify(userdn, modlist)
        client.unbind()
        return True

    except (AttributeError, LDAPError), e:
        logger.critical("Unable to change password on ldap server.")
        logger.critical(e)
        return False

