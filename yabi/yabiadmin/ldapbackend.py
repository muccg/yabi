from django.contrib.auth.models import User
from yabiadmin import settings
from yabiadmin import ldaputils       

class LDAPBackend:

    def authenticate(self, username=None, password=None):
        if self.is_valid_ldap_user(username, password):
            return self.get_db_user(username) or self.create_db_user(username)

    def is_valid_ldap_user(self, username, password):
        try:
            userdn = ldaputils.get_userdn_of(username)

            if ldaputils.can_bind_as(userdn, password) and \
                    ldaputils.is_user_member_of(userdn, settings.AUTH_LDAP_ADMIN_GROUP):
                return True
        except ldap.LDAPError, err:
            print "Ldap Error:"
            print err

        return False

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

