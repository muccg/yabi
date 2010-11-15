import ldap

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

