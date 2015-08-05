import logging
import kerberos
from django.conf import settings
from yabi.authbackends.ldap import LDAPBackend

logger = logging.getLogger(__name__)


class KerberosLDAPBackend(LDAPBackend):
    MANDATORY_SETTINGS = LDAPBackend.MANDATORY_SETTINGS + ('AUTH_KERBEROS_REALM',)

    def can_log_in(self, username, password):
        try:
            return kerberos.checkPassword(username.lower(), password, settings.AUTH_KERBEROS_SERVICE, settings.AUTH_KERBEROS_REALM)
        except:
            logger.exception("Failure during Kerberos authentication")
            return False
