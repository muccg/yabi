from yabiadmin.yabi.models import *
from yabiadmin.yabi.forms import *
from django.contrib import admin
from django.contrib.webservices.ext import ExtJsonInterface
from django.forms.models import BaseInlineFormSet
from django.forms import ModelForm
from django import forms

class AdminBase(ExtJsonInterface, admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not isinstance(obj, Base): 
            return form.save()

        instance = form.save(commit=False)
        if not change:
            instance.created_by = request.user
        instance.last_modified_by = request.user
        instance.save()
        form.save_m2m()
        return instance

    def save_formset(self, request, form, formset, change):
        if not issubclass(formset.model, Base):
            return formset.save()

        def set_user(instance):
            if instance.pk is None:
                instance.created_by = request.user
            instance.last_modified_by = request.user
            instance.save()

        instances = formset.save(commit=False)
        map(set_user, instances)
        formset.save_m2m()
        return instances

class ToolGroupingInline(admin.TabularInline):
    model = ToolGrouping
    extra = 1

class ToolOutputExtensionInline(admin.TabularInline):
    model = ToolOutputExtension
    extra = 1



class ToolParameterFormset(BaseInlineFormSet):

    def get_queryset(self):
        return super(ToolParameterFormset, self).get_queryset().order_by('id')

    def add_fields(self, form, index):
        super(ToolParameterFormset, self).add_fields(form, index)
        tool_only_queryset = ToolParameter.objects.filter(tool=self.instance)
        form.fields["source_param"].queryset = tool_only_queryset
        form.fields["extension_param"].queryset = tool_only_queryset


class ToolParameterInline(admin.StackedInline):
    model = ToolParameter
    formset = ToolParameterFormset
    extra = 3

class ToolAdmin(AdminBase):
    form = ToolForm
    list_display = ['name', 'display_name', 'path', 'enabled', 'backend', 'fs_backend', 'tool_groups_str', 'tool_link', 'created_by', 'created_on']
    inlines = [ToolOutputExtensionInline, ToolParameterInline] # need to add back in tool groupings and find out why it is not working with mango
    search_fields = ['name', 'display_name', 'path']
    save_as = True

    def get_form(self, request, obj=None, **kwargs):
        return ToolForm

class ToolGroupAdmin(AdminBase):
    list_display = ['name', 'tools_str']
    inlines = [ToolGroupingInline]

class ToolSetAdmin(AdminBase):
    list_display = ['name', 'users_str']

class FileTypeAdmin(AdminBase):
    list_display = ['name']

class QueueAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_name', 'created_on']

class CredentialAdmin(AdminBase):
    list_display = ['description', 'user', 'username']
    list_filter = ['user']

    
class BackendAdmin(AdminBase):
    form = BackendForm
    list_display = ['name', 'description', 'scheme', 'hostname', 'port', 'path', 'uri', 'backend_summary_link']

class UserAdmin(AdminBase):
    list_display = ['name', 'toolsets_str', 'tools_link', 'backends_link']

class BackendCredentialAdmin(AdminBase):
    form = BackendCredentialForm
    list_display = ['backend', 'credential', 'homedir', 'visible', 'default_stageout']
    list_filter = ['credential__user']
    
class ParameterSwitchUseAdmin(AdminBase):
    list_display = ['display_text', 'formatstring', 'description']
    search_fields = ['display_text', 'description']

admin.site.register(FileExtension, AdminBase)
admin.site.register(ParameterSwitchUse, ParameterSwitchUseAdmin)
#admin.site.register(QueuedWorkflow, QueueAdmin)
#admin.site.register(InProgressWorkflow, QueueAdmin)
admin.site.register(FileType, FileTypeAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(ToolGroup, ToolGroupAdmin)
admin.site.register(ToolSet, ToolSetAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Credential, CredentialAdmin)
admin.site.register(BackendCredential, BackendCredentialAdmin)
admin.site.register(Backend, BackendAdmin)
