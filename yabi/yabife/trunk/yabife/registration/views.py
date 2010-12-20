from django.contrib.auth.models import User as DjangoUser
from django.db import transaction
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.utils import webhelpers
from json import dumps

from yabife.yabifeapp.models import Appliance, User

from forms import RegistrationForm
from models import Request


@transaction.commit_on_success
def confirm(request, key):
    req = get_object_or_404(Request, confirmation_key=key)
    req.confirm(request)

    return render_to_response("registration/confirm.html", {
        "h": webhelpers,
    })

@transaction.commit_on_success
def index(request):
    terms = dict([(a.id, a.tos) for a in Appliance.objects.all()])

    context = {
        "h": webhelpers,
        "terms": dumps(terms),
    }

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        context["form"] = form

        if form.is_valid():
            try:
                username = form.cleaned_data["username"]
                email = form.cleaned_data["email"]

                user = DjangoUser.objects.create_user(username, email)

                user.first_name = form.cleaned_data["first_name"]
                user.last_name = form.cleaned_data["last_name"]
                user.is_active = False
                user.save()

                profile = User.objects.create(user=user, appliance=form.cleaned_data["appliance"])

                req = Request.objects.create(user=user)

                # Send e-mail.
                message = render_to_string("registration/email/confirm.txt", {
                    "first_name": form.cleaned_data["first_name"],
                    "url": request.build_absolute_uri(webhelpers.url("/registration/confirm/%s" % req.confirmation_key)),
                })
                user.email_user("YABI Account Request Confirmation", message)

                context["email"] = email
                return render_to_response("registration/success.html", context)
            except IntegrityError, e:
                transaction.rollback()
                form.add_error("username", "The username is already in use.")
            except Exception, e:
                transaction.rollback()
                form.add_global_error(unicode(e))

    else:
        form = RegistrationForm()
        context["form"] = form

    return render_to_response("registration/index.html", context)
