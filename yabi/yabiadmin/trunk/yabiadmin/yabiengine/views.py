from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import webhelpers
from django.utils import simplejson as json
from yabiadmin.yabiengine.models import Task, Job, Workflow

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


def status(request, model=None, id=None, status=None):

    models = {'task':Task, 'job':Job, 'workflow':Workflow}

    try:

        if request.method == "GET":

            # sanity checks
            if not model or not id or model.lower() not in models.keys():
                raise ObjectDoesNotExist()

            m = models[model.lower()]
            obj = m.objects.get(id=id)

            return HttpResponse(json.dumps({"status":obj.status}))

        else:

            # check we have required params
            for key in ["model", "id", "status"]:
                if key not in request.POST:
                    raise ObjectDoesNotExist()

            model = str(request.POST["model"]).lower()
            id = int(request.POST["id"])
            status = str(request.POST["status"])
                
            if model not in models.keys():
                raise ObjectDoesNotExist()
            
            m = models[model]
            obj = m.objects.get(id=id)
            obj.status=status
            obj.save()

            return HttpResponse("Thanks!")

    except (ObjectDoesNotExist,ValueError):
        return HttpResponseNotFound("Object not found")
