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

import base64
from functools import partial
import ldap
import hashlib
import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

try:
    from ldap import LDAPError, MOD_REPLACE
    from .ldapclient import LDAPClient
    settings.LDAP_IN_USE = True
except ImportError as e:
    settings.LDAP_IN_USE = False
    if settings.AUTH_LDAP_SERVER:
        logger.info("LDAP modules not imported. If you are not using LDAP this is not a problem.")


class LDAPUser(object):
    def __init__(self, dn, user_data):
        self.dn = dn
        self._data = user_data

        self.uid = _first_attr_value(user_data, settings.AUTH_LDAP_USERNAME_ATTR)
        self.username = self.uid
        self.email = _first_attr_value(user_data, settings.AUTH_LDAP_EMAIL_ATTR)
        self.first_name = _first_attr_value(user_data, settings.AUTH_LDAP_FIRSTNAME_ATTR)
        self.last_name = _first_attr_value(user_data, settings.AUTH_LDAP_LASTNAME_ATTR)
        self.member_of = []
        if settings.AUTH_LDAP_MEMBER_OF_ATTR:
            groups = user_data.get(settings.AUTH_LDAP_MEMBER_OF_ATTR)
            if groups is not None and len(groups) > 0:
                self.member_of = groups

    @property
    def full_name(self):
        return ' '.join([self.first_name, self.last_name])

    def is_member_of(self, groupdn):
        """Returns True if the user contains memberOf reference to the group passed in.

        This takes into account only groups listed on the User object.
        For user membership defined on group objects another search has to be done on Groups.
        """
        for group in self.member_of:
            if are_dns_equal(groupdn, group):
                return True
        return False


class LDAPUserDoesNotExist(ObjectDoesNotExist):
    pass


# TODO all these functions make an ldap connection
# They should at least accept the ldapclient optionally so one
# can reuse the same connection if doing multiple operations


def get_all_yabi_users():
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)

    def result_to_LDAPUser(result):
        dn, data = result
        return LDAPUser(dn, data)

    all_users = map(result_to_LDAPUser, ldapclient.search(settings.AUTH_LDAP_USER_BASE, settings.AUTH_LDAP_USER_FILTER))

    yabi_user_dns = _get_yabi_userdns().union(_get_yabi_admin_userdns())

    def is_yabi_user(user):
        return (user.dn in yabi_user_dns or
                user.is_member_of(settings.AUTH_LDAP_YABI_GROUP_DN) or
                user.is_member_of(settings.AUTH_LDAP_YABI_ADMIN_GROUP_DN))

    yabi_users = filter(is_yabi_user, all_users)

    return yabi_users


def _get_userdns_in_group(groupdn):
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    MEMBER_ATTR = settings.AUTH_LDAP_MEMBER_ATTR
    try:
        result = ldapclient.search(groupdn, '%s=*' % MEMBER_ATTR, [MEMBER_ATTR])
    except ldap.NO_SUCH_OBJECT:
        logger.warning("Required group '%s' doesn't exist in LDAP" % groupdn)
        result = []

    if len(result) > 0:
        first_result = result[0]
        data_dict = first_result[1]
    else:
        data_dict = {}

    return set(data_dict.get(MEMBER_ATTR, []))


# These aren't public because they just get the users defined in the LDAP groups
# The other part of the picture are users that define groups on the user object.
# The get_all_yabi_users() above, and the is_user_in_group() + related functions
# below takes into account both possibilites so are safe to use.
_get_yabi_userdns = partial(_get_userdns_in_group, settings.AUTH_LDAP_YABI_GROUP_DN)
_get_yabi_admin_userdns = partial(_get_userdns_in_group, settings.AUTH_LDAP_YABI_ADMIN_GROUP_DN)


def get_user(username):
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    userfilter = "(%s=%s)" % (settings.AUTH_LDAP_USERNAME_ATTR, username)

    result = ldapclient.search(settings.AUTH_LDAP_USER_BASE, userfilter)
    if len(result) == 0:
        raise LDAPUserDoesNotExist
    if len(result) == 1:
        return LDAPUser(*result[0])
    else:
        msg = "Searched at base '%s' with userfilter '%s', returned %s " + \
              "results instead of 0 or 1. Results were: \n%s"
        msg = msg % (settings.AUTH_LDAP_USER_BASE, userfilter, len(result), result)
        raise ImproperlyConfigured(msg)


def update_yabi_user(django_user, ldap_user):
    django_user.username = ldap_user.username
    django_user.email = ldap_user.email
    django_user.first_name = ldap_user.first_name
    django_user.last_name = ldap_user.last_name

    django_user.is_superuser = is_user_in_yabi_admin_group(ldap_user)
    django_user.is_staff = django_user.is_superuser
    django_user.save()


def create_yabi_user(ldap_user):
    django_user = User.objects.create_user(ldap_user.username)
    update_yabi_user(django_user, ldap_user)

    return django_user


def can_bind_as(userdn, password):
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    try:
        if ldapclient.bind_as(userdn, password):
            return True

        return False
    finally:
        ldapclient.unbind()


def is_user_in_group(groupdn, user):
    if user.is_member_of(groupdn):
        return True
    ldapclient = LDAPClient(settings.AUTH_LDAP_SERVER)
    groupfilter = '(%s=%s)' % (settings.AUTH_LDAP_MEMBER_ATTR, user.dn)
    try:
        result = ldapclient.search(groupdn, groupfilter, ['cn'])
    except ldap.NO_SUCH_OBJECT:
        logger.warning("Required group '%s' doesn't exist in LDAP" % groupdn)
        return False
    return len(result) == 1


is_user_in_yabi_group = partial(is_user_in_group,
                                settings.AUTH_LDAP_YABI_GROUP_DN)
is_user_in_yabi_admin_group = partial(is_user_in_group,
                                      settings.AUTH_LDAP_YABI_ADMIN_GROUP_DN)


# TODO is this general enough?
# Why do we md5 directly? The ldap client should take care of the encryption.
def set_ldap_password(username, current_password, new_password, bind_userdn=None, bind_password=None):

    assert current_password, "No currentPassword was supplied."
    assert new_password, "No newPassword was supplied."

    try:
        user = get_user(username)
        client = LDAPClient(settings.AUTH_LDAP_SERVER)

        if bind_userdn and bind_password:
            client.bind_as(bind_userdn, bind_password)
        else:
            client.bind_as(user.dn, current_password)

        md5 = hashlib.md5(new_password).digest()
        modlist = (
            (MOD_REPLACE, "userPassword", "{MD5}%s" % (base64.encodestring(md5).strip(), )),
        )
        client.modify(user.dn, modlist)
        client.unbind()
        return True

    except (AttributeError, LDAPError) as e:
        logger.critical("Unable to change password on ldap server.")
        logger.critical(e)
        return False


def are_dns_equal(dn, other_dn):
    return ldap.dn.str2dn(dn.lower()) == ldap.dn.str2dn(other_dn.lower())


def _first_attr_value(d, attr, default=''):
    values = d.get(attr)
    if values is None or len(values) == 0:
        return default
    return values[0]
