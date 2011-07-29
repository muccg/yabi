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
from django.conf.urls.defaults import *
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import webhelpers
from models import Request
from yabife.yabifeapp.models import User


class RequestAdmin(ModelAdmin):
    actions = ["approve", "deny"]
    list_display = ("user", "state")
    list_filter = ("state",)

    # Custom views to allow for simple approve/deny links.
    def get_urls(self):
        urls = super(RequestAdmin, self).get_urls()

        local_urls = patterns("",
            (r"^approve/([0-9]+)[/]*$", self.admin_site.admin_view(self.approve_view)),
            (r"^deny/([0-9]+)[/]*$", self.admin_site.admin_view(self.deny_view)),
        )

        return local_urls + urls

    @transaction.commit_on_success
    def approve_view(self, request, id):
        req = get_object_or_404(Request, id=id)
        req.approve(request)

        self.message_user(request, "Request for %s approved." % unicode(req))
        return HttpResponseRedirect(webhelpers.url("/admin/registration/request/"))

    @transaction.commit_on_success
    def deny_view(self, request, id):
        req = get_object_or_404(Request, id=id)
        req.deny(request)

        self.message_user(request, "Request for %s denied." % unicode(req))
        return HttpResponseRedirect(webhelpers.url("/admin/registration/request/"))

    # Admin actions allowing bulk approval or denial.
    def get_actions(self, request):
        actions = super(RequestAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions

    @transaction.commit_on_success
    def approve(self, request, qs):
        approved = []
        skipped = []
        failed = []

        for req in qs:
            if req.state == 1:
                try:
                    req.approve(request)
                    approved.append(unicode(req))
                except User.LDAPUserDoesNotExist:
                    failed.append("%s (no LDAP account)" % unicode(req))
            else:
                skipped.append(unicode(req))

        message = {
            "approved": (", ".join(approved)) if approved else "None",
            "skipped": (", ".join(skipped)) if skipped else "None",
            "num_approved": len(approved),
            "num_skipped": len(skipped),
        }

        if failed:
            transaction.rollback()

            message["failed"] = ", ".join(failed)
            message["num_failed"] = len(failed)

            messages.error(request, """
%(num_failed)d request(s) FAILED: %(failed)s.
 %(num_approved)d request(s) would have succeeded;
 %(num_skipped)d request(s) would have been skipped.
""" % message)
        else:
            self.message_user(request, """
%(num_approved)d request(s) approved;
 %(num_skipped)d request(s) skipped (either already approved or not yet confirmed).
 Approved requests: %(approved)s.
 Skipped requests: %(skipped)s.
""" % message)

    approve.short_description = "Approve selected requests"

    @transaction.commit_on_success
    def deny(self, request, qs):
        denied = []
        skipped = []

        for req in qs:
            if req.state < 2:
                req.deny(request)
                denied.append(unicode(req))
            else:
                skipped.append(unicode(req))

        message = {
            "denied": (", ".join(denied)) if denied else "None",
            "skipped": (", ".join(skipped)) if skipped else "None",
            "num_denied": len(denied),
            "num_skipped": len(skipped),
        }

        self.message_user(request, """
%(num_denied)d request(s) denied;
 %(num_skipped)d request(s) skipped (already approved).
 Denied requests: %(denied)s.
 Skipped requests: %(skipped)s.
""" % message)
    deny.short_description = "Deny selected requests"


def register(site):
    site.register(Request, RequestAdmin)
