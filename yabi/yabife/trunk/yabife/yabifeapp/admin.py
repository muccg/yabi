from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.webservices.ext import ExtJsonInterface
from yabife.yabifeapp.models import Appliance, ApplianceAdministrator, User


class SuperuserOnlyModelAdmin(ModelAdmin):
    def queryset(self, request):
        if request.user.is_superuser:
            return self.model.objects.all()

        return self.model.objects.none()


class ApplianceAdministratorAdmin(TabularInline):
    model = ApplianceAdministrator
 
class ApplianceAdmin(ExtJsonInterface, SuperuserOnlyModelAdmin):
    inlines = [ApplianceAdministratorAdmin]
    list_display = ("name", "url")


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
