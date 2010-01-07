# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import webhelpers
from django.utils import simplejson as json
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog
from django.conf import settings
import wfwrangler

import logging
import yabilogging
logger = logging.getLogger('yabiengine')

from conf import config

def task(request):
    logger.debug('')
    
    # we need to see if the host requesting the task is the host that is allowed to request it (the one configured in our settings or config file)
    ipaddress = request.META[ "HTTP_X_FORWARDED_FOR" if "HTTP_X_FORWARDED_FOR" in request.META else "REMOTE_ADDR" ]
    logger.debug("Task request originating from: %s"%ipaddress)
    
    if "origin" not in request.REQUEST:
        logger.critical("IP %s requested task but had no origin identifier set."%ipaddress)
        return HttpResponseServerError("Error requesting task. No origin identifier set.")
    
    # get sender id
    origin = request.REQUEST["origin"]
    
    # verify that the requesters origin is correct
    ip,port = origin.split(":")
    exp_ip, exp_port = config.config['backend']['port']
    
    if ip != exp_ip or port != exp_port:
        return HttpResponseServerError("Error requesting task. Origin incorrect. This is not the admin you are looking for")
       
    #if config.config['backend']['ip'] != ip and 
    
    try:
        tasks = Task.objects.filter(status=settings.STATUS["ready"])

        if tasks:
            task = tasks[0]
            task.status=settings.STATUS["requested"]
            task.save()
            return HttpResponse(task.json())
        else:
            raise ObjectDoesNotExist("No more tasks")  
        
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found.")
    except Exception, e:
        logger.critical("Caught Exception:")
        logger.critical(e)
        return HttpResponseServerError("Error requesting task.")

def status(request, model, id):
    logger.debug('')
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
                raise HttpResponseServerError("POST request to error service should contain 'message' parameter\n")

            model = str(model).lower()
            id = int(id)
            status = str(request.POST["status"])

            # truncate status to 64 chars to avoid any sql field length errors
            status = status[:64]
                
            m = models[model]
            obj = m.objects.get(id=id)
            obj.status=status
            obj.save()

            #TODO return something sensible here
            return HttpResponse("Thanks!")

    except (ObjectDoesNotExist,ValueError):
        return HttpResponseNotFound("Object not found")
    except Exception, e:
        import traceback
        print "!!!!",traceback.format_exc()
        logger.critical("Caught Exception: %s" % e)
        return HttpResponseServerError(e)


def error(request, table, id):
    logger.debug('')
    
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
                return HttpResponseServerError("POST request to error service should contain 'message' parameter\n")

            syslog = Syslog(table_name=str(table),
                            table_id=int(id),
                            message=str(request.POST["message"])
                            )

            syslog.save()

            return HttpResponse("Thanks!")

    except (ObjectDoesNotExist,ValueError):
        return HttpResponseNotFound("Object not found")
    except Exception, e:
        logger.critical("Caught Exception: %s" % e.message)
        return HttpResponseNotFound("Object not found")
