# Create your views here.
import httplib
from urllib import urlencode
from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponse
from django.conf import settings
from django.utils.webhelpers import url
from django.shortcuts import render_to_response, get_object_or_404

# mako template support
from django.shortcuts import render_to_response, render_mako

def index(request):
    return render_mako('index.mako', s=settings, request=request)

# proxy view to pass through all requests set up in urls.py
def proxy(request, url):

    if not url.startswith("/"):
        url = "/" + url

    if request.method == "GET":

        resource = "%s%s" % (url, urlencode(request.GET))
        conn = httplib.HTTPConnection(settings.YABIADMIN_SERVER)
        conn.request(request.method, resource)
        r = conn.getresponse()

    elif request.method == "POST":

        resource = "%s" % url
        data = urlencode(request.POST)
        headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}

        conn = httplib.HTTPConnection(settings.YABIADMIN_SERVER)
        conn.request(request.method, resource, data, headers)
        r = conn.getresponse()

    return HttpResponse(r.read(),status=int(r.status))
