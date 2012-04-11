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
from django.conf import settings
from django.contrib.auth.models import SiteProfileNotAvailable, User as DjangoUser
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from ccg.utils import webhelpers

from datetime import datetime, timedelta
from uuid import uuid4


class Request(models.Model):
    STATES = (
        (0, "Requested; awaiting user confirmation"),
        (1, "User confirmed; awaiting sysadmin activation"),
        (2, "Active"),
    )

    user = models.OneToOneField(DjangoUser)
    state = models.PositiveSmallIntegerField(choices=STATES, default=0)
    confirmation_key = models.CharField(max_length=32, default=lambda: Request.create_key())
    request_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("state", "user__username")

    def __unicode__(self):
        return unicode(self.user)

    def approve(self, request):
        password = DjangoUser.objects.make_random_password()

        self.user.is_active = True

        # TODO rewrite this to use set_password
        # change the profiles to set password in the correct way ie model vs ldap
        assert False, "Not yet implemented"
        
##        self.user.get_profile().set_ldap_password(current_password="",
##                                                  new_password=password,
##                                                  bind_userdn=settings.AUTH_LDAP_PASSWORD_CHANGE_USERDN,
##                                                  bind_password=settings.AUTH_LDAP_PASSWORD_CHANGE_PASSWORD)

        self.user.save()

        message = render_to_string("registration/email/approved.txt", {
            "password": password,
            "request": self,
            "url": request.build_absolute_uri(webhelpers.url("/")),
            "user": self.user,
        })
        self.user.email_user("YABI Account Approved", message)

        self.state = 2
        self.save()

    def confirm(self, request):
        self.state = 1
        self.save()

        message = render_to_string("registration/email/approve.txt", {
            "base": request.build_absolute_uri(webhelpers.url("/admin/registration/request/")),
            "request": self,
            "user": self.user,
        })

        emails = [admin[1] for admin in settings.ADMINS]
        send_mail("YABI Account Request", message, settings.DEFAULT_FROM_EMAIL, emails)

    def deny(self, request):
        message = render_to_string("registration/email/denied.txt", {
            "emails": settings.ADMINS,
            "request": self,
            "url": request.build_absolute_uri(webhelpers.url("/")),
            "user": self.user,
        })
        self.user.email_user("YABI Account Denied", message)

        self.user.delete()

    @staticmethod
    def create_key():
        return uuid4().hex

    @staticmethod
    def get_expired():
        request_ttl = settings.get("REGISTRATION_REQUEST_TTL", 604800)
        expiry_time = datetime.now() - timedelta(seconds=request_ttl)

        return Request.objects.filter(request_time__lt=expiry_time, state=0)
