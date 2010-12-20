# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User as DjangoUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from ldap import LDAPError, MOD_REPLACE
from urlparse import urlparse
from yabife.ldapclient import LDAPClient
from yabife.ldaputils import get_userdn_of

import base64
import hashlib

class Appliance(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=200, verbose_name="URL")
    tos = models.TextField(verbose_name="terms of service")

    def __unicode__(self):
        if self.name:
            return self.name

        return self.url

    @property
    def host(self):
        return urlparse(self.url).hostname
        
    @property
    def port(self):
        return urlparse(self.url).port

    @property
    def path(self):
        return urlparse(self.url).path

    class Meta:
        ordering = ["name", "url"]


class ApplianceAdministrator(models.Model):
    appliance = models.ForeignKey(Appliance)
    name = models.CharField(max_length=200)
    email = models.EmailField()

    def __unicode__(self):
        return "%s <%s>" % (self.name, self.email)

    class Meta:
        ordering = ["appliance", "name"]


class User(models.Model):
    user = models.OneToOneField(DjangoUser)
    appliance = models.ForeignKey(Appliance)
    user_option_access = models.BooleanField(default=True)
    credential_access = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s: %s" % (self.user.username, self.appliance.url)

    class Meta:
        ordering = ["user__username"]

    class LDAPUserDoesNotExist(ObjectDoesNotExist):
        pass

    def get_userdn(self):
        userdn = get_userdn_of(self.user.username)

        if not userdn:
            raise User.LDAPUserDoesNotExist

        return userdn

    def has_account_tab(self):
        return self.user_option_access or self.credential_access

    def set_ldap_password(self, current_password, new_password, bind_userdn=None, bind_password=None):
        userdn = self.get_userdn()
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
