# -*- coding: utf-8 -*-
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
# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core import urlresolvers
from django.utils import webhelpers
from django.db import transaction 
from django.utils import simplejson as json
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from yabiadmin.yabiengine.tasks import walk
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog
from yabiadmin.yabiengine.enginemodels import EngineTask, EngineJob, EngineWorkflow

import logging
logger = logging.getLogger(__name__)

from constants import *

def task(request):
    if "tasktag" not in request.REQUEST:
        return HttpResponseServerError("Error requesting task. No tasktag identifier set.")
    
    # verify that the requesters tasktag is correct
    tasktag = request.REQUEST["tasktag"]
    if tasktag != settings.TASKTAG:
        logger.critical("Task requested  had incorrect identifier set. Expected tasktag %s but got %s instead." % (settings.TASKTAG, tasktag))
        return HttpResponseServerError("Error requesting task. Tasktag incorrect. This is not the admin you are looking for.")
       
    try:
        # only expose tasks that are ready and are intended for the expeceted backend
        tasks = Task.objects.filter(status=STATUS_READY, tasktag=tasktag)

        if tasks:
            task = tasks[0]
            task.status=STATUS_REQUESTED
            task.save()
            logger.debug('requested task id: %s command: %s' % (task.id, task.command))
            return HttpResponse(task.json())
        else:
            raise ObjectDoesNotExist("No more tasks")  
        
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found.")
    except Exception, e:
        logger.critical("Caught Exception:")
        import traceback
        logger.critical(e)
        logger.critical(traceback.format_exc())
        return HttpResponseServerError("Error requesting task.")

def blockedtask(request):
    if "tasktag" not in request.REQUEST:
        return HttpResponseServerError("Error requesting task. No tasktag identifier set.")
    
    # verify that the requesters tasktag is correct
    tasktag = request.REQUEST["tasktag"]
    if tasktag != settings.TASKTAG:
        logger.critical("Task requested  had incorrect identifier set. Expected tasktag %s but got %s instead." % (settings.TASKTAG, tasktag))
        return HttpResponseServerError("Error requesting task. Tasktag incorrect. This is not the admin you are looking for.")
       
    try:
        # only expose tasks that are ready and are intended for the expeceted backend
        tasks = Task.objects.filter(status=STATUS_RESUME, tasktag=tasktag)

        print "TASKS",tasks

        if tasks:
            task = tasks[0]
            task.status=STATUS_REQUESTED
            task.save()
            logger.debug('requested resumption task id: %s command: %s' % (task.id, task.command))
            return HttpResponse(task.json())
        else:
            raise ObjectDoesNotExist("No more tasks")  
        
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found. Bleck!")
    except Exception, e:
        logger.critical("Caught Exception:")
        import traceback
        logger.critical(e)
        logger.critical(traceback.format_exc())
        return HttpResponseServerError("Error requesting task.")

@transaction.commit_on_success
def status(request, model, id):
    logger.debug('model: %s id: %s' % (model, id))
    models = {'task':EngineTask, 'job':EngineJob, 'workflow':EngineWorkflow}

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
                return HttpResponseServerError("POST request to status service should contain 'status' parameter\n")

            model = str(model).lower()
            id = int(id)
            status = str(request.POST["status"])

            logger.debug("status="+request.POST['status'])

            # truncate status to 64 chars to avoid any sql field length errors
            status = status[:64]
                
            m = models[model]
            obj = m.objects.get(id=id)
            obj.status=status
            if status != STATUS_BLOCKED and status!= STATUS_RESUME:
                obj.percent_complete = STATUS_PROGRESS_MAP[status]
            obj.save()

            # update the job status when the task status changes
            if (model == 'task'):
                obj.job.update_status()
                obj.job.save()

            if status in [STATUS_READY, STATUS_COMPLETE, STATUS_ERROR]:
                # always commit transactions before sending tasks depending on state from the current transaction http://docs.celeryq.org/en/latest/userguide/tasks.html
                transaction.commit()

                # trigger a walk via celery 
                walk.delay(workflow_id=obj.workflow_id)

            return HttpResponse("")

    except (ObjectDoesNotExist,ValueError):
        return HttpResponseNotFound("Object not found")
    except Exception, e:
        import traceback
        logger.critical(traceback.format_exc())
        logger.critical("Caught Exception: %s" % e)
        return HttpResponseServerError(e)

def remote_id(request,id):
    logger.debug('remote_task_id> %s'%id)
    try:
        if "remote_id" not in request.POST:
            return HttpResponseServerError("POST request to remote_id service should contain 'remote_id' parameter\n")

        id = int(id)
        remote_id = str(request.POST["remote_id"])

        logger.debug("remote_id="+request.POST['remote_id'])

        # truncate status to 256 chars to avoid any sql field length errors
        remote_id = remote_id[:256]

        obj = EngineTask.objects.get(id=id)
        obj.remote_id = remote_id
        obj.save()

        return HttpResponse("")
    except (ObjectDoesNotExist,ValueError):
        return HttpResponseNotFound("Object not found")
    except Exception, e:
        import traceback
        logger.critical(traceback.format_exc())
        logger.critical("Caught Exception: %s" % e)
        return HttpResponseServerError(e)

def remote_info(request,id):
    logger.debug('remote_task_info> %s'%id)
    try:
        if "remote_info" not in request.POST:
            return HttpResponseServerError("POST request to remote_info service should contain 'remote_info' parameter\n")

        id = int(id)
        remote_info = str(request.POST["remote_info"])

        logger.debug("remote_info="+request.POST['remote_info'])

        # truncate status to 2048 chars to avoid any sql field length errors
        remote_info = remote_info[:2048]

        obj = EngineTask.objects.get(id=id)
        obj.remote_info = remote_info
        obj.save()

        return HttpResponse("")
    except (ObjectDoesNotExist,ValueError):
        return HttpResponseNotFound("Object not found")
    except Exception, e:
        import traceback
        logger.critical(traceback.format_exc())
        logger.critical("Caught Exception: %s" % e)
        return HttpResponseServerError(e)

def error(request, table, id):
    logger.debug('table: %s id: %s' % (table, id))
    
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


def job(request, workflow, order):
    try:
        workflow = EngineWorkflow.objects.get(id=int(workflow))
        job = EngineJob.objects.get(workflow=workflow, order=int(order))

        # Put some fields of general interest in.
        output = {
            "id": job.id,
            "status": job.status,
            "tasks": [],
        }

        for task in job.task_set.all():
            try:
                remote_info = json.loads(task.remote_info)
            except (TypeError, ValueError):
                # JSON failed to decode or was null.
                remote_info = None

            output["tasks"].append({
                "id": task.id,
                "percent_complete": task.percent_complete,
                "remote_id": task.remote_id,
                "remote_info": remote_info,
            })

        return HttpResponse(json.dumps(output), mimetype="application/json")
    except (MultipleObjectsReturned, ObjectDoesNotExist, ValueError):
        return HttpResponseNotFound("Object not found")
    except Exception, e:
        logger.critical("Caught Exception: %s" % e.message)
        return HttpResponseNotFound("Object not found")


@staff_member_required
def task_json(request, task):
    logger.debug("task_json> %s" % task)

    try:
        task = Task.objects.get(id=int(task))
        return HttpResponse(content=task.json(), content_type="application/json; charset=UTF-8")
    except (ObjectDoesNotExist, ValueError):
        return HttpResponseNotFound("Task not found")


@staff_member_required
def workflow_summary(request, workflow_id):
    logger.debug('')

    workflow = get_object_or_404(Workflow, pk=workflow_id)
   
    return render_to_response('yabiengine/workflow_summary.html', {
        'w': workflow,
        'user':request.user,
        'title': 'Workflow Summary',
        'root_path':urlresolvers.reverse('admin:index'),
        'settings':settings
        })
