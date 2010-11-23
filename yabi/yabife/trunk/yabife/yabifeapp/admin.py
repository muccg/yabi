from django.contrib.admin import ModelAdmin
from django.contrib.webservices.ext import ExtJsonInterface
from yabife.yabifeapp.models import Appliance, User


class SuperuserOnlyModelAdmin(ModelAdmin):
    def queryset(self, request):
        if request.user.is_superuser:
            return self.model.objects.all()

        return self.model.objects.none()


class ApplianceAdmin(ExtJsonInterface, SuperuserOnlyModelAdmin):
    pass

 
class UserAdmin(ExtJsonInterface, SuperuserOnlyModelAdmin):
    fieldsets = (
        (None, {
            "fields": ("user", "appliance"),
        }),
        ("Permissions", {
            "fields": ("user_option_access", "credential_access"),
        }),
    )
    list_display = ("user", "appliance")


def register(site):
    site.register(Appliance, ApplianceAdmin)
    site.register(User, UserAdmin)
