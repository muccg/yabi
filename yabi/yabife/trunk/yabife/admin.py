from django.contrib import admin
from yabife.yabifeapp.admin import register

site = admin.AdminSite(name="Yabi Frontend Administration")
register(site)
