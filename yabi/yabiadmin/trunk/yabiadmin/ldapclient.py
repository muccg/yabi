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
import ldap
from yabiadmin import settings

class LDAPClient:
    def __init__(self, servers, userdn=None, password=None):
        self._servers = servers
        self._userdn = userdn
        self._password = password

    def bind_to_server(self, server, userdn, password):
        self._ldap = ldap.initialize(server)
        self._ldap.protocol_version = ldap.VERSION3
        if userdn:
            self._ldap.simple_bind_s(userdn, password)
        else:
            self._ldap.simple_bind_s()

    def bind_as(self, userdn=None, password=None):
        for server in self._servers:
            try:
                self.bind_to_server(server, userdn, password)
                return True
            except ldap.LDAPError, e:
                print "Ldap Error while binding to server %s:" % server
                print e
        return False       

    def search(self, base, search_for, retr_attrs=None):
        if not hasattr(self, '_ldap'):
            self.bind_as(self._userdn, self._password) 
        try:
            result = self._ldap.search_s(base, ldap.SCOPE_SUBTREE, search_for, retr_attrs)
            return result
        finally:
            self.unbind()

    def unbind(self):
        if hasattr(self, '_ldap'):
            self._ldap.unbind()
        del(self._ldap)

