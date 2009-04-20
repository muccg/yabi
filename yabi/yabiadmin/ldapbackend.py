import ldap
from django.contrib.auth.models import User
from yabiadmin import settings
       
class LDAPBackend:

    def authenticate(self, username=None, password=None):
        if self.is_valid_ldap_user(username, password):
            return self.get_db_user(username) or self.create_db_user(username)

    def is_valid_ldap_user(self, username, password):
        try:
            userdn = self.get_userdn_of(username)

            if self.can_bind_as(userdn, password) and \
                    self.is_user_member_of(userdn, settings.AUTH_LDAP_ADMIN_GROUP):
                return True
        except ldap.LDAPError, err:
            print "Ldap Error:"
            print err

        return False

    def get_userdn_of(self, username):
        ldapclient = LDAPClient(settings.AUTH_LDAP_SERVERS)
        userfilter = "(&(objectclass=person) (uid=%s))" % username
        result = ldapclient.search(settings.AUTH_LDAP_BASE, ldap.SCOPE_SUBTREE, userfilter, ['dn'])
        if result and len(result) == 1:
            return result[0][0]

    def can_bind_as(self, userdn, password):
        ldapclient = LDAPClient(settings.AUTH_LDAP_SERVERS)
        try:
            if ldapclient.bind_as(userdn, password):
                return True
        finally:
            ldapclient.unbind()

    def is_user_member_of(self, userdn, groupname):
        ldapclient = LDAPClient(settings.AUTH_LDAP_SERVERS)
        groupfilter = '(&(objectClass=groupofuniquenames)(uniqueMember=%s)(cn=%s))' % (userdn, groupname)
        result = ldapclient.search(settings.AUTH_LDAP_GROUP_BASE, ldap.SCOPE_SUBTREE, groupfilter, ['cn'])
        return len(result) == 1

    def get_db_user(self, username):
        try:
            return User.objects.get(username__exact=username)
        except User.DoesNotExist:
            return None

    def create_db_user(self, username):
        user = User.objects.create_user(username,"")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

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

    def search(self, *arg, **kwargs):
        if not hasattr(self, '_ldap'):
            self.bind_as(self._userdn, self._password) 
        result = self._ldap.search_s(*arg, **kwargs)
        self.unbind()
        return result

    def unbind(self):
        if hasattr(self, '_ldap'):
            self._ldap.unbind()
        del(self._ldap)


