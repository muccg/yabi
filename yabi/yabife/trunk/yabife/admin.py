from django.contrib import admin
from django.contrib.webservices.ext import ExtJsonInterface

import django.contrib.auth.admin
import django.contrib.auth.models
import django.contrib.sites.admin
import django.contrib.sites.models

import yabife.registration.admin
import yabife.yabifeapp.admin


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


site = admin.AdminSite(name="Yabi Frontend Administration")

# Django Auth.
site.register(django.contrib.auth.models.Group, GroupAdmin)
site.register(django.contrib.auth.models.User, UserAdmin)

yabife.registration.admin.register(site)
yabife.yabifeapp.admin.register(site)
