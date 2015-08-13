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

from django.contrib import admin

import django.contrib.auth.admin
import django.contrib.auth.models
import django.contrib.sites.admin
import django.contrib.sites.models
import yabi.admin
import yabiengine.admin


# Overrides for the default django.contrib.auth ModelAdmin subclasses that
# include the JSON mixin.
class GroupAdmin(django.contrib.auth.admin.GroupAdmin):
    def queryset(self, request):
        if request.user.is_superuser:
            return django.contrib.auth.models.Group.objects.all()

        return django.contrib.auth.models.Group.objects.none()


class UserAdmin(django.contrib.auth.admin.UserAdmin):
    def queryset(self, request):
        if request.user.is_superuser:
            return django.contrib.auth.models.User.objects.all()

        return django.contrib.auth.models.User.objects.none()


# Create the local site.
site = admin.AdminSite()

# Django Auth.
site.register(django.contrib.auth.models.Group, GroupAdmin)
site.register(django.contrib.auth.models.User, UserAdmin)

# Django Sites, we're not using sites but you can turn them on here
# site.register(django.contrib.sites.models.Site, django.contrib.sites.admin.SiteAdmin)

# Yabi Admin.
yabi.admin.register(site)

# Yabi Engine.
yabiengine.admin.register(site)
