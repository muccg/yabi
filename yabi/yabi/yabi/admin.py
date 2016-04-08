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
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from ccg_django_utils import webhelpers

from yabi.yabi import models as m
from yabi.yabi import forms as f


class AdminBase(admin.ModelAdmin):
    save_as = True

    def save_model(self, request, obj, form, change):
        if not isinstance(obj, m.Base):
            obj.save()

        if not change:
            obj.created_by = request.user
        obj.last_modified_by = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        if not issubclass(formset.model, m.Base):
            formset.save()

        def set_user(instance):
            if instance.pk is None:
                instance.created_by = request.user
            instance.last_modified_by = request.user
            instance.save()

        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for inst in instances:
            set_user(inst)
        formset.save_m2m()


class ToolGroupingInline(admin.TabularInline):
    model = m.ToolGrouping
    extra = 1


class ToolOutputExtensionInline(admin.TabularInline):
    model = m.ToolOutputExtension
    form = f.ToolOutputExtensionForm
    extra = 1
    fields = ['file_extension']


class ToolParameterFormset(BaseInlineFormSet):

    def get_queryset(self):
        return super(ToolParameterFormset, self).get_queryset().order_by('id')

    def add_fields(self, form, index):
        super(ToolParameterFormset, self).add_fields(form, index)


class ToolParameterInline(admin.StackedInline):
    form = f.ToolParameterForm
    model = m.ToolParameter
    formset = ToolParameterFormset
    extra = 3
    filter_horizontal = ['accepted_filetypes']

    def get_formset(self, request, obj=None, **kwargs):
        # squirrel away tool object so it can be used in the filter
        # for use_output_filename.
        self.parent_tool = obj
        return super(ToolParameterInline, self).get_formset(
            request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "use_output_filename":
            toolparams = db_field.rel.to.objects.all()
            toolparams = toolparams.filter(tool=self.parent_tool)
            kwargs["queryset"] = toolparams

        return super(
            ToolParameterInline, self).formfield_for_foreignkey(
                db_field, request, **kwargs)


class ToolDescAdmin(AdminBase):
    list_display = ['name', 'tool_link',
                    'created_by', 'created_on']
    inlines = [ToolOutputExtensionInline, ToolParameterInline]
    search_fields = ['name']
    save_as = False

    def tool_link(self, ob):
        view_url = reverse('tool_view', kwargs={'tool_id': ob.id})
        return '<a href="%s">View</a>' % view_url
    tool_link.short_description = 'View'
    tool_link.allow_tags = True


class ToolAdmin(AdminBase):
    form = f.ToolForm
    list_display = ['desc', 'path', 'display_name', 'view_json', 'tool_groups_str', 'backend', 'fs_backend', 'enabled']
    search_fields = ['desc__name', 'display_name', 'path']
    save_as = False
    list_filter = ["backend", "fs_backend", "enabled"]

    def tool_groups_str(self, ob):
        def fmt(tg):
            return "%s (%s)" % (tg.tool_group, tg.tool_set)
        return ",".join(map(fmt, ob.toolgrouping_set.all()))
    tool_groups_str.short_description = 'Belongs to Tool Groups'

    def view_json(self, ob):
        view_url = reverse('tool', kwargs={'toolid': ob.id}) + '?admin_access=true'
        return '<a href="%s">View JSON</a>' % view_url
    view_json.short_description = 'View JSON'
    view_json.allow_tags = True


class ToolGroupAdmin(AdminBase):
    list_display = ['name', 'tools_str']
    inlines = [ToolGroupingInline]
    save_as = False


class ToolSetAdmin(AdminBase):
    list_display = ['name', 'users_str']
    filter_horizontal = ['users']


class FileTypeAdmin(AdminBase):
    list_display = ['name', 'file_extensions_text']
    search_fields = ['name']
    filter_horizontal = ['extensions']


class FileExtensionAdmin(AdminBase):
    list_display = ['pattern']
    search_fields = ['pattern']


class CredentialAdmin(AdminBase):
    form = f.CredentialForm
    list_display = ['description', 'user', 'username']
    list_filter = ['user']
    actions = ['duplicate_credential', 'cache_credential', 'decache_credential']
    search_fields = ['description', 'username', 'user__user__username']
    readonly_fields = ['security_state']
    fields = (("auth_class", "description"),
              ("username", "password"), "key",
              "user", "expires_on", "security_state", "caps")

    class Media:
        js = ("javascript/yabifixer.js",)

    def get_form(self, request, obj=None, **kwargs):
        form = super(CredentialAdmin, self).get_form(request, obj, **kwargs)
        from ..backend import BaseBackend
        form.base_fields['auth_class'].choices = [("", "Any")] + BaseBackend.get_auth_class_choices()
        form.base_fields['auth_class'].initial = obj.guess_backend_auth_class() if obj else ""
        return form

    def duplicate_credential(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect(webhelpers.url("/ws/manage_credential/?ids=%s&action=duplicate" % (",".join(selected))))
    duplicate_credential.short_description = "Duplicate selected credentials."

    def cache_credential(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect(webhelpers.url("/ws/manage_credential/?ids=%s&action=cache" % (",".join(selected))))
    cache_credential.short_description = "Cache selected credentials in memory."

    def decache_credential(self, request, queryset):
        success, fail = 0, 0
        for credential in queryset:
            access = credential.get_credential_access()
            if access.in_cache:
                access.clear_cache()
                success += 1
            else:
                fail += 1

        self.message_user(request, "%d credential%s successfully purged from cache." % (success, "s" if success != 1 else ""))
        if fail:
            self.message_user(request, "%d credential%s failed purge." % (fail, "s" if fail != 1 else ""))
    decache_credential.short_description = "Purge selected credentials from cache."


class DynamicBackendConfigurationAdmin(AdminBase):
    form = f.DynamicBackendConfigurationForm
    list_display = ['name']


class BackendAdmin(AdminBase):
    form = f.BackendForm
    list_display = ['name', 'description', 'scheme', 'hostname',
                    'port', 'path', 'uri', 'backend_summary_link']
    fieldsets = (
        (None, {
            'fields': ('name', 'dynamic_backend', 'dynamic_backend_configuration',
                       'description', 'scheme', 'hostname', 'port', 'path', 'caps')
        }),
        ('Filesystem Backends', {
            'classes': ('fsbackend-only',),
            'fields': ('lcopy_supported', 'link_supported')
        }),
        ('Execution Backends', {
            'classes': ('execbackend-only',),
            'fields': ('submission', 'temporary_directory', 'tasks_per_user')
        }),
    )

    class Media:
        js = ("javascript/yabifixer.js",)

    def backend_summary_link(self, obj):
        return '<a href="%s">View</a>' % obj.get_absolute_url()

    backend_summary_link.short_description = 'Summary'
    backend_summary_link.allow_tags = True


class UserAdmin(AdminBase):
    list_display = ['user', 'user_option_access', 'credential_access', 'toolsets_str', 'tools_link', 'backends_link', 'last_login']
    list_editable = ['user_option_access', 'credential_access']


class BackendCredentialAdmin(AdminBase):
    form = f.BackendCredentialForm
    list_display = ['backend', 'credential', 'homedir', 'visible', 'default_stageout']
    list_filter = ['credential__user']
    raw_id_fields = ['credential']


class ParameterSwitchUseAdmin(AdminBase):
    list_display = ['display_text', 'formatstring', 'description']
    search_fields = ['display_text', 'description']


class HostKeyAdmin(AdminBase):
    list_display = ['hostname', 'key_type', 'fingerprint', 'allowed']
    search_fields = ['hostname', 'key_type', 'fingerprint']
    list_filter = ['hostname', 'key_type']
    fields = ['hostname', 'allowed', 'key_type', 'data']


def register(site):
    site.register(m.FileExtension, FileExtensionAdmin)
    site.register(m.ParameterSwitchUse, ParameterSwitchUseAdmin)
    site.register(m.FileType, FileTypeAdmin)
    site.register(m.ToolDesc, ToolDescAdmin)
    site.register(m.Tool, ToolAdmin)
    site.register(m.ToolGroup, ToolGroupAdmin)
    site.register(m.ToolSet, ToolSetAdmin)
    site.register(m.User, UserAdmin)
    site.register(m.Credential, CredentialAdmin)
    site.register(m.BackendCredential, BackendCredentialAdmin)
    site.register(m.Backend, BackendAdmin)
    site.register(m.DynamicBackendConfiguration, DynamicBackendConfigurationAdmin)
    site.register(m.HostKey, HostKeyAdmin)
