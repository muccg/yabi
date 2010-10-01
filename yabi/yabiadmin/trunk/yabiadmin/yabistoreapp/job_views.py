import os
import shutil
from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response, get_object_or_404, render_mako
from django.core.exceptions import ObjectDoesNotExist
from django.utils import webhelpers
from django.utils import simplejson as json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
#from models import *

# our storage
import db

import logging
logger = logging.getLogger('yabistore')




def job(request, username):
    logger.debug('')
    return HttpResponse('Not yet implemented')

def job_id(request, username, id=None):
    logger.debug('')
    return HttpResponse('Not yet implemented')
