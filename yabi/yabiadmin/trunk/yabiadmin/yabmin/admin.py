from yabiadmin.yabmin.models import *
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.forms import ModelForm
from django import forms

class AdminBase(admin.ModelAdmin):
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
    extra = 3

class ToolParameterFormset(BaseInlineFormSet):
    def get_queryset(self):
        return super(ToolParameterFormset, self).get_queryset().order_by('id')

    def add_fields(self, form, index):
        super(ToolParameterFormset, self).add_fields(form, index)
        tool_only_queryset = ToolParameter.objects.filter(tool=self.instance)
        form.fields["source_param"].queryset = tool_only_queryset
        form.fields["extension_param"].queryset = tool_only_queryset

class ToolParameterInline(admin.TabularInline):
    model = ToolParameter
    formset = ToolParameterFormset
    extra = 3

class ToolRslExtensionModuleInline(admin.TabularInline):
    model = ToolRslExtensionModule
    extra = 3

class ToolRslArgumentOrderFormset(BaseInlineFormSet):
    def get_queryset(self):
        return super(ToolRslArgumentOrderFormset, self).get_queryset().order_by('rank')

class ToolRslArgumentOrderInline(admin.TabularInline):
    model = ToolRslArgumentOrder
    formset = ToolRslArgumentOrderFormset
    extra = 7

class ToolRslInfoAdmin(AdminBase):
    list_display = ['tool_name', 'executable']
    inlines = [ToolRslArgumentOrderInline, ToolRslExtensionModuleInline]

class ToolForm(ModelForm):
    class Meta:
        model = Tool
        exclude = ('groups','output_filetypes')

    def __init__(self, *args, **kwargs):
        super(ToolForm, self).__init__(*args, **kwargs)
        self.fields["batch_on_param"].queryset = ToolParameter.objects.filter(tool=self.instance)

class ToolAdmin(AdminBase):
    list_display = ['name', 'enabled', 'backend', 'tool_groups_str', 'tool_link', 'created_by', 'created_on']
    inlines = [ToolOutputExtensionInline, ToolParameterInline] # need to add back in tool groupings and find out why it is not working with mango

    def get_form(self, request, obj=None, **kwargs):
        return ToolForm

class ToolGroupAdmin(AdminBase):
    list_display = ['name', 'tools_str']
    inlines = [ToolGroupingInline]

class ToolSetAdmin(AdminBase):
    list_display = ['name', 'users_str']

class UserAdmin(AdminBase):
    list_display = ['name', 'toolsets_str', 'tools_link']

class FileTypeAdmin(AdminBase):
    list_display = ['name']

class QueueAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_name', 'created_on']


class BackendInline(admin.TabularInline):
    model = BackendCredential
    extra = 3


class CredentialAdmin(AdminBase):
    list_display = ['description', 'user', 'username']
    inlines = [BackendInline]

class BackendAdmin(AdminBase):
    list_display = ['name', 'description']


admin.site.register(FileExtension, AdminBase)
admin.site.register(ParameterFilter, AdminBase)
admin.site.register(ParameterSwitchUse, AdminBase)
#admin.site.register(QueuedWorkflow, QueueAdmin)
#admin.site.register(InProgressWorkflow, QueueAdmin)
admin.site.register(FileType, FileTypeAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(ToolGroup, ToolGroupAdmin)
admin.site.register(ToolSet, ToolSetAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(ToolRslInfo, ToolRslInfoAdmin)
admin.site.register(Credential, CredentialAdmin)
admin.site.register(Backend, BackendAdmin)
