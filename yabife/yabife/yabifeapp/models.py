# -*- coding: utf-8 -*-
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
# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from ldap import LDAPError, MOD_REPLACE
from urlparse import urlparse
from yabife.ldapclient import LDAPClient
from yabife.ldaputils import get_userdn_of
from utils import yabiadmin_passchange

from django.contrib import logging
logger = logging.getLogger('yabife')

import base64
import hashlib

class Appliance(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=200, verbose_name="URL", help_text="Full URL to appliance ending with a / i.e. https://hostname.edu.au/yabiadmin/")
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

    class Meta:
        ordering = ["user__username"]

    def __unicode__(self):
        return "%s: %s" % (self.user.username, self.appliance.url)

    def has_account_tab(self):
        return self.user_option_access or self.credential_access


class ModelBackendUser(User):

    class Meta:
        proxy = True

    def change_password(self, request):
        """Return a tuple of (valid, errormsg)"""

        currentPassword = request.POST.get("currentPassword", None)
        newPassword = request.POST.get("newPassword", None)
        confirmPassword = request.POST.get("confirmPassword", None)

        # check the user is allowed to change password
        if not self.user_option_access:
            return (False, "You do not have access to this web service")

        # check we have everything
        if not currentPassword or not newPassword or not confirmPassword:
            return (False, "Either the current, new or confirmation password is missing from request.")

        # check the current password
        if not authenticate(username=request.user.username, password=currentPassword):
            return (False, "Current password is incorrect")

        # the new passwords should at least match and meet whatever rules we decide
        # to impose (currently a minimum six character length)
        if newPassword != confirmPassword:
            return (False, "The new passwords must match")

        if len(newPassword) < 6:
            return (False, "The new password must be at least 6 characters in length")

        # this is the model backend so we have to change the password in the db
        self.user.set_password(newPassword)
        
        # if all this succeeded we should tell the middleware to do the same
        # TODO catch exception here and return appropriately
        yabiadmin_passchange(request, currentPassword, newPassword)

        self.user.save()

        return (True, "Password changed successfully")

    
class LDAPBackendUser(User):

    class Meta:
        proxy = True

    def change_password(self, request):
        """Return a tuple of (valid, errormsg)"""

        currentPassword = request.POST.get("currentPassword", None)
        newPassword = request.POST.get("newPassword", None)
        confirmPassword = request.POST.get("confirmPassword", None)

        # check the user is allowed to change password
        if not self.user_option_access:
            return (False, "You do not have access to this web service")

        # check we have everything
        if not currentPassword or not newPassword or not confirmPassword:
            return (False, "Either the current, new or confirmation password is missing from request.")

        # check the current password
        if not authenticate(username=request.user.username, password=currentPassword):
            return (False, "Current password is incorrect")

        # the new passwords should at least match and meet whatever rules we decide
        # to impose (currently a minimum six character length)
        if newPassword != confirmPassword:
            return (False, "The new passwords must match")

        if len(newPassword) < 6:
            return (False, "The new password must be at least 6 characters in length")

        # this is an ldap model backend, so we don't change the Auth.User password

        # if all this succeeded we should tell the middleware to do the same
        # TODO catch exception here and return appropriately
        yabiadmin_passchange(request, currentPassword, newPassword)

        self.user.save()

        return (True, "Password changed successfully")
