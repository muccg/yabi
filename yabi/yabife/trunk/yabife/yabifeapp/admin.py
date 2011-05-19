### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
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
