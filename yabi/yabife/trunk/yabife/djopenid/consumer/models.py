# (c) Copyright 2007 Thomas Bohmbach, Jr.  All Rights Reserved. 
#
# See the LICENSE file that should have been included with this distribution
# for more specific information.

from django.contrib.auth.models import User
from django.db import models


class UserOpenID(models.Model):
    """
    Associates an openid (URL) to a user object
    """
    user = models.ForeignKey(User, related_name="openids")
    openid_url = models.URLField(unique=True)
    
    class Admin:
        search_fields = ['user']
        list_display = ('user', 'openid_url')

class OpenIDRegistration(models.Model):
    name = models.TextField(null=True, blank=True)
    openid_url = models.TextField(null=True, blank=True)
    organisation = models.TextField(null=True, blank=True)
    faculty = models.TextField(null=True, blank=True)
    user_type = models.TextField(null=True, blank=True)
    org_user_id = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    contact_number = models.TextField(null=True, blank=True)
    supervisor_name = models.TextField(null=True, blank=True)
    supervisor_number = models.TextField(null=True, blank=True)
    supervisor_email = models.TextField(null=True, blank=True)
    project_title = models.TextField(null=True, blank=True)
    project_description = models.TextField(null=True, blank=True)
    rfcd_code_1 = models.TextField(null=True, blank=True)
    rfcd_code_1_weight = models.TextField(null=True, blank=True)
    rfcd_code_2 = models.TextField(null=True, blank=True)
    rfcd_code_2_weight = models.TextField(null=True, blank=True)
    rfcd_code_3 = models.TextField(null=True, blank=True)
    rfcd_code_3_weight = models.TextField(null=True, blank=True)
    resources_compute = models.TextField(null=True, blank=True)
    resources_data = models.TextField(null=True, blank=True)
    resources_network = models.TextField(null=True, blank=True)
    estimate = models.TextField(null=True, blank=True)
    describe = models.TextField(null=True, blank=True)
    software_needs = models.TextField(null=True, blank=True)
    agreement = models.TextField(null=True, blank=True)

    class Admin:
        search_fields = ['name', 'email']
        list_display = ('name', 'openid_url', 'organisation', 'email')    

class OpenIDBackend:
    """
    Authenticate against models.UserOpenID
    """
    def authenticate(self, openid_url=None):
        if openid_url:
            try:
                user_openid = UserOpenID.objects.get(openid_url=openid_url)
                return user_openid.user
            except UserOpenID.DoesNotExist:
                return None
        else:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None