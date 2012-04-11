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
from django.contrib.auth.models import User as DjangoUser
from django.db import transaction
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from ccg.utils import webhelpers
from django.conf import settings

from yabiadmin.yabifeapp.models import User

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

    context = {
        "h": webhelpers,
        "terms": settings.TERMS_OF_SERVICE,
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

                profile = User.objects.create(user=user)

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
