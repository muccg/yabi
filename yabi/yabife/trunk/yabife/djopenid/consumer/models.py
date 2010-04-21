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