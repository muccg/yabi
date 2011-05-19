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
from django.contrib import admin
from django.contrib.webservices.ext import ExtJsonInterface

import django.contrib.auth.admin
import django.contrib.auth.models
import django.contrib.sites.admin
import django.contrib.sites.models
import yabiadmin.yabi.admin
import yabiadmin.yabiengine.admin


# Overrides for the default django.contrib.auth ModelAdmin subclasses that
# include the JSON mixin.
class GroupAdmin(ExtJsonInterface, django.contrib.auth.admin.GroupAdmin):
    def queryset(self, request):
        if request.user.is_superuser:
            return django.contrib.auth.models.Group.objects.all()

        return django.contrib.auth.models.Group.objects.none()

class UserAdmin(ExtJsonInterface, django.contrib.auth.admin.UserAdmin):
    def queryset(self, request):
        if request.user.is_superuser:
            return django.contrib.auth.models.User.objects.all()

        return django.contrib.auth.models.User.objects.none()


# Create the local site.
site = admin.AdminSite()

# Django Auth.
site.register(django.contrib.auth.models.Group, GroupAdmin)
site.register(django.contrib.auth.models.User, UserAdmin)

# Django Sites.
site.register(django.contrib.sites.models.Site, django.contrib.sites.admin.SiteAdmin)

# Yabi Admin. 
yabiadmin.yabi.admin.register(site)

# Yabi Engine.
yabiadmin.yabiengine.admin.register(site)
