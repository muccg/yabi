from django.contrib.auth.models import User as DjangoUser
from django.db import models


class Appliance(models.Model):
    url = models.CharField(max_length=200, verbose_name="URL")

    def __unicode__(self):
        return self.url

    class Meta:
        ordering = ["url"]


class User(models.Model):
    user = models.OneToOneField(DjangoUser)
    appliance = models.ForeignKey(Appliance)

    def __unicode__(self):
        return "%s: %s" % (self.user.username, self.appliance.url)

    class Meta:
        ordering = ["user__username"]
