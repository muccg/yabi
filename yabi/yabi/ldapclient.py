# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ldap
from django.conf import settings
import logging
logger = logging.getLogger(__name__)


if not settings.AUTH_LDAP_REQUIRE_TLS_CERT:
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)


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
            except ldap.LDAPError as e:
                logger.error("Ldap Error while binding to server %s:" % server)
                logger.error(e)
        return False

    def modify(self, dn, modlist, serverctrls=None, clientctrls=None):
        self._ldap.modify_ext_s(dn, modlist, serverctrls, clientctrls)

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
