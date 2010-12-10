# -*- coding: utf-8 -*-
from django.contrib.auth.models import User as DjangoUser
from django.db import models
from urlparse import urlparse

class Appliance(models.Model):
    url = models.CharField(max_length=200, verbose_name="URL")

    def __unicode__(self):
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
        ordering = ["url"]


class User(models.Model):
    user = models.OneToOneField(DjangoUser)
    appliance = models.ForeignKey(Appliance)
    user_option_access = models.BooleanField(default=True)
    credential_access = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s: %s" % (self.user.username, self.appliance.url)

    class Meta:
        ordering = ["user__username"]

    def has_account_tab(self):
        return self.user_option_access or self.credential_access
