from django.conf import settings
from django.contrib.auth.models import SiteProfileNotAvailable, User as DjangoUser
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import webhelpers

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
        self.user.get_profile().set_ldap_password(current_password="",
                                                  new_password=password,
                                                  bind_userdn=settings.AUTH_LDAP_PASSWORD_CHANGE_USERDN,
                                                  bind_password=settings.AUTH_LDAP_PASSWORD_CHANGE_PASSWORD)
        self.user.save()

        appliance = self.user.get_profile().appliance
        message = render_to_string("registration/email/approved.txt", {
            "appliance": appliance,
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

        appliance = self.user.get_profile().appliance
        message = render_to_string("registration/email/approve.txt", {
            "appliance": appliance,
            "base": request.build_absolute_uri(webhelpers.url("/admin/registration/request/")),
            "request": self,
            "user": self.user,
        })

        emails = [admin.email for admin in appliance.applianceadministrator_set.all()]
        send_mail("YABI Account Request", message, settings.DEFAULT_FROM_EMAIL, emails)

    def deny(self, request):
        appliance = self.user.get_profile().appliance
        message = render_to_string("registration/email/denied.txt", {
            "appliance": appliance,
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
