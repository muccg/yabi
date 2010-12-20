from django.conf.urls.defaults import *

import views


urlpatterns = patterns("",
    (r"^confirm/([0-9a-f]+)[/]*$", views.confirm),
    (r"^[/]*$", views.index),
)
