from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import webhelpers
from django.utils import simplejson as json
from yabiadmin.yabiengine.models import Task

def task(request):

    try:
        tasks = Task.objects.all()

        if tasks:
            task = tasks[0]
            return HttpResponse(task.json())
        else:
            raise ObjectDoesNotExist()
        
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")

