from yabiadmin.yabmin.models import ToolType, Tool, ToolParameter, ToolGroup, ToolGrouping, ToolSet, User, FileExtension, FileType
from django.contrib import admin

class ToolGroupingInline(admin.TabularInline):
    model = ToolGrouping
    extra = 1

class ToolParameterInline(admin.TabularInline):
    model = ToolParameter
    extra = 3

class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled', 'tool_groups_str', 'created_by', 'created_on']
    inlines = [ToolParameterInline, ToolGroupingInline]

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
admin.site.register(ToolType)
admin.site.register(FileType, FileTypeAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(ToolGroup, ToolGroupAdmin)
admin.site.register(ToolSet, ToolSetAdmin)
admin.site.register(User, UserAdmin)

