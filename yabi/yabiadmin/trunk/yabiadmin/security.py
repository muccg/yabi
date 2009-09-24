from django.http import HttpResponse, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from urlparse import urlparse
from yabiadmin.utils import json_error
from yabiadmin.yabmin.models import BackendCredential


def validate_user(f):
    """
    Decorator that should be applied to all functions which take a username. It will check this username
    against the yabiusername that the proxy has injected into the GET or POST object
    """
    def check_user(request, username, *args, **kwargs):

        if request.method == 'GET':
            if 'yabiusername' not in request.GET or request.GET['yabiusername'] != username:
                return HttpResponseForbidden(json_error("Trying to view resource for different user."))

        elif request.method == 'POST':
            if 'yabiusername' not in request.POST or request.POST['yabiusername'] != username:
                return HttpResponseForbidden(json_error("Trying to view resource for different user."))

        return f(request,username, *args, **kwargs)
    return check_user


def validate_uri(f):
    """
    Decorator that should be applied to all functions which take a uri. It will check the uri for a username that
    matches the yabiusername in the GET or POST object
    """
    def check_uri(request, *args, **kwargs):

        uri = None
        yabiusername = None
        
        if request.method == 'GET':
            if 'uri' in request.GET:
                uri = request.GET['uri']
            if 'yabiusername' in request.GET:
                yabiusername = request.GET['yabiusername']
                
        elif request.method == 'POST':
            if 'uri' in request.POST:
                uri = request.POST['uri']
            if 'yabiusername' in request.POST:
                yabiusername = request.POST['yabiusername']

        if uri:
            try:

                scheme, rest = uri.split(":",1) # split required for non RFC uris ie gridftp, yabifs
                u = urlparse(rest)

                # find a matching credential based on uri
                # check that credentials yabiusername matches that passed from front end
                bc = BackendCredential.objects.get(backend__hostname=u.hostname,
                                                   backend__scheme=scheme,
                                                   credential__username=u.username)

                if bc.credential.user.name != yabiusername:
                    return HttpResponseForbidden(json_error("Trying to view uri for different user."))

            except ObjectDoesNotExist, e:
                return HttpResponseForbidden(json_error("No backend credential found."))                

            except ValueError, e:
                return HttpResponseForbidden(json_error("Invalid URI."))
            

        return f(request, *args, **kwargs)
    return check_uri

