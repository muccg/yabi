# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from urlparse import urlparse
from yabiadmin.utils import json_error
from yabiadmin.yabi.models import BackendCredential

from yabiadmin.yabiengine import backendhelper

def validate_user(f):
    """
    Decorator that should be applied to all functions which take a username. It will check this username
    against the yabiusername that the proxy has injected into the GET or POST object
    """
    def check_user(request, *args, **kwargs):

        username = None
        if 'username' in kwargs:
            username = kwargs['username']
        elif 'username' in request.POST:
            username = request.POST['username']

        if request.method == 'GET':
            if 'yabiusername' not in request.GET or request.GET['yabiusername'] != username:
                return HttpResponseForbidden(json_error("Trying to view resource for different user."))

        elif request.method == 'POST':
            if 'yabiusername' not in request.POST or request.POST['yabiusername'] != username:
                return HttpResponseForbidden(json_error("Trying to view resource for different user."))

        return f(request, *args, **kwargs)
    return check_user


def validate_uri(f):
    """
    Decorator that should be applied to all functions which take a uri.

    It applies the following checks:

    1. The supplied yabiusername matches the username associated with the credential for the uri
    2. The start of the uri's path matches the path allowed for the user based on backend.path and backendcredential.homedir
    """
    def check_uri(request, *args, **kwargs):

        uri = None
        yabiusername = None

        if 'uri' in request.GET:
            uri = request.GET['uri']
        elif 'uri' in request.POST:
            uri = request.POST['uri']

        if 'yabiusername' in request.GET:
            yabiusername = request.GET['yabiusername']
        elif 'yabiusername' in request.POST:
            yabiusername = request.POST['yabiusername']

        try:

            if uri:
                if not yabiusername:
                    raise ValueError

                bc = backendhelper.get_backendcredential_for_uri(yabiusername, uri)
                

                scheme, rest = uri.split(":",1) # split required for non RFC uris ie gridftp, yabifs
                u = urlparse(rest)

                ## find a matching credential based on uri
                #bc = BackendCredential.objects.get(backend__hostname=u.hostname,
                                                   #backend__scheme=scheme,
                                                   #credential__username=u.username)

                # check that credentials yabiusername matches that passed from front end
                if bc.credential.user.name != yabiusername:
                    return HttpResponseForbidden(json_error("Trying to view uri for different user."))

                # check that the start of the path matches what the user has access to
                validpath = bc.backend.path + bc.homedir
                if not u.path.startswith(validpath):
                    return HttpResponseForbidden(json_error("Invalid path."))


        except ObjectDoesNotExist, e:
            return HttpResponseForbidden(json_error("No backend credential found."))

        except ValueError, e:
            return HttpResponseForbidden(json_error("Invalid URI."))
        
        return f(request, *args, **kwargs)
    return check_uri

