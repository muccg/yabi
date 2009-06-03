# Create your views here.
from django.conf import settings
from django.utils.webhelpers import url
from django.shortcuts import render_to_response, get_object_or_404

# mako template support
from django.shortcuts import render_to_response, render_mako

def index(request):
    return render_mako('index.mako', s=settings, request=request)

def tool(request, toolname):
    return render_mako('tool.mako', s=settings, request=request, toolname=toolname)
