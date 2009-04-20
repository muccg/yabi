from yabiadmin.yabmin.models import ToolType, Tool, ToolParameter, ToolGroup, ToolGrouping, ToolSet, User, FileExtension, FileType, ParameterFilter, ParameterSwitchUse, ToolRslInfo, ToolRslExtensionModule, ToolRslArgumentOrder, ToolOutputExtension
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.forms import ModelForm
from django import forms

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
    extra = 7

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

class ToolRslInfoAdmin(admin.ModelAdmin):
    list_display = ['tool_name', 'executable']
    inlines = [ToolRslArgumentOrderInline, ToolRslExtensionModuleInline]

class ToolForm(ModelForm):
    class Meta:
        model = Tool
        exclude = ('groups','output_filetypes')

    def __init__(self, *args, **kwargs):
        super(ToolForm, self).__init__(*args, **kwargs)
        self.fields["batch_on_param"].queryset = ToolParameter.objects.filter(tool=self.instance)

class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled', 'type', 'tool_groups_str', 'tool_link', 'created_by', 'created_on']
    inlines = [ToolOutputExtensionInline, ToolParameterInline, ToolGroupingInline]

    def get_form(self, request, obj=None, **kwargs):
        return ToolForm

class ToolGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'tools_str']
    inlines = [ToolGroupingInline]

class ToolSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'users_str']

class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'toolsets_str', 'tools_link']

class FileTypeAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(FileExtension)
admin.site.register(ParameterFilter)
admin.site.register(ParameterSwitchUse)
admin.site.register(ToolType)
admin.site.register(FileType, FileTypeAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(ToolGroup, ToolGroupAdmin)
admin.site.register(ToolSet, ToolSetAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(ToolRslInfo, ToolRslInfoAdmin)

