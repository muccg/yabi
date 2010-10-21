from django.contrib.admin import ModelAdmin
from yabife.yabifeapp.models import Appliance, User


class ApplianceAdmin(ModelAdmin):
    pass

 
class UserAdmin(ModelAdmin):
    list_display = ("user", "appliance")


def register(site):
    site.register(Appliance, ApplianceAdmin)
    site.register(User, UserAdmin)
