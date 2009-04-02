from yabiadmin.yabmin.models import ToolType, Tool, ToolParameter, ToolGroup, ToolGrouping, ToolSet, User, FileExtension, FileType, ParameterFilter, ParameterSwitchUse, ToolRslInfo, ToolRslExtensionModule, ToolRslArgumentOrder, ToolOutputExtension
from django.contrib import admin

class ToolGroupingInline(admin.TabularInline):
    model = ToolGrouping
    extra = 1

class ToolOutputExtensionInline(admin.TabularInline):
    model = ToolOutputExtension
    extra = 3

class ToolParameterInline(admin.TabularInline):
    model = ToolParameter
    extra = 7

class ToolRslExtensionModuleInline(admin.TabularInline):
    model = ToolRslExtensionModule
    extra = 3

class ToolRslArgumentOrderInline(admin.TabularInline):
    model = ToolRslArgumentOrder
    extra = 7

class ToolRslInfoAdmin(admin.ModelAdmin):
    list_display = ['executable']
    inlines = [ToolRslArgumentOrderInline, ToolRslExtensionModuleInline]

class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled', 'type', 'tool_groups_str', 'created_by', 'created_on']
    inlines = [ToolOutputExtensionInline, ToolParameterInline, ToolGroupingInline]

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

