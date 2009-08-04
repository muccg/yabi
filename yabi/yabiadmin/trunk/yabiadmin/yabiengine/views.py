from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import webhelpers
from django.utils import simplejson as json
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog
from django.conf import settings
import wfwrangler
import logging
logger = logging.getLogger('yabiengine')

def task(request):

    try:
        tasks = Task.objects.filter(status=settings.STATUS["ready"])

        if tasks:
            task = tasks[0]
            task.status=settings.STATUS["requested"]
            task.save()
            return HttpResponse(task.json())
        else:
            raise ObjectDoesNotExist()
        
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")


def status(request, model, id):
    logger.info('status')

    models = {'task':Task, 'job':Job, 'workflow':Workflow}

    # sanity checks
    if model.lower() not in models.keys():
        raise ObjectDoesNotExist()

    try:

        if request.method == "GET":

            m = models[model.lower()]
            obj = m.objects.get(id=id)

            return HttpResponse(json.dumps({"status":obj.status}))

        else:

            if "status" not in request.POST:
                raise ObjectDoesNotExist()

            model = str(model).lower()
            id = int(id)
            status = str(request.POST["status"])

            # truncate status to 64 chars to avoid any sql field length errors
            status = status[:64]
                
            m = models[model]
            obj = m.objects.get(id=id)
            obj.status=status
            obj.save()

            # trigger the workflow walk
            if isinstance(obj, Job):
                wfwrangler.walk(obj.workflow)

            return HttpResponse("Thanks!")

    except (ObjectDoesNotExist,ValueError):
        return HttpResponseNotFound("Object not found")


def error(request, table, id):

    try:

        if request.method == "GET":
            entries = Syslog.objects.filter(table_name=table, table_id=id)

            if not entries:
                raise ObjectDoesNotExist()

            output = [{"table_name":x.table_name, "table_id":x.table_id, "message":x.message} for x in entries]
            return HttpResponse(json.dumps(output))

        else:

            # check we have required params
            if "message" not in request.POST:
                raise ObjectDoesNotExist()

            syslog = Syslog(table_name=str(table),
                            table_id=int(id),
                            message=str(request.POST["message"])
                            )

            syslog.save()

            return HttpResponse("Thanks!")

    except (ObjectDoesNotExist,ValueError):
        return HttpResponseNotFound("Object not found")
