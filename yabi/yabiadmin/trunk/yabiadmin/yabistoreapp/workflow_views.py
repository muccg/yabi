# -*- coding: utf-8 -*-
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


def index(request):
    logger.debug('')
    return HttpResponse("yabistore V0.1")


def workflows_for_user(request, username):
    logger.debug('')
    db.ensure_user_db(username)

    if request.method == 'GET':
        # get all workflows for a user
        result = db.get_workflows( username )
        return HttpResponse(json.dumps(db.get_workflows( username )),mimetype='application/json')

    return HttpResponseServerError('Unsupported request method\n')


def get_add_or_update_workflow(request, username, workflow_id):
    logger.debug('')
    db.ensure_user_db(username)

    if not workflow_id or not username:
        return HttpResponseNotFound('No workflow_id or no username supplied.\n')

    if request.method == 'POST': 
        try:
            logger.debug("POST received with: %s"%request.POST.keys())
            taglist = []
            if 'taglist' in request.POST:
                taglist = request.POST['taglist'].split(',')

            # check if workflow exists
            workflow = None
            try:
                workflow = db.get_workflow(username, int(workflow_id))
            except db.NoSuchWorkflow, e:
                pass

            if not workflow:
                id=db.save_workflow(username, int(workflow_id), request.POST['json'], request.POST['status'], request.POST['name'], taglist)
            
            else:

                # build our description of updating
                updateset = {}
                for key in db.WORKFLOW_VARS:
                    if key != 'id':             # don't overwrite id
                        if key in request.POST:
                            updateset[key] = request.POST[key]

                # and the taglist
                if taglist:
                    db.update_workflow(username,int(workflow_id),updateset,taglist)
                else:
                    #dont update the taglist with this set
                    db.update_workflow(username,int(workflow_id),updateset)
    
        except db.NoSuchWorkflow, e:
            logger.critical('%s' % e)
            return HttpResponseNotFound(e)
            
        return HttpResponse("Success")
                                        
    elif request.method == 'GET':
        try:
            workflow = db.get_workflow(username,int(workflow_id))
    
        except (ObjectDoesNotExist, Exception), e:
            logger.critical('%s' % e)
            return HttpResponseNotFound(e)
            
        return HttpResponse(json.dumps(workflow),
                                        mimetype='application/json')
                                        
    return HttpResponseServerError('Unsupported request method\n')



def delete_workflow(request, username, workflow_id):
    logger.debug('')
    db.ensure_user_db(username)

    if not workflow_id or not username:
        return HttpResponseNotFound('No workflow_id or no username supplied.\n')

    try:
        db.delete_workflow(username, int(workflow_id))
        return HttpResponse("Success")
    except:
        return HttpResponseServerError('Unable to delete workflow.\n')


def workflow_id_tags(request, username, id=None):
    logger.debug('')
    db.ensure_user_db(username)
    
    if not id or not username:
        return HttpResponseNotFound('No id or no username supplied.\n')

    if request.method == 'POST': 
        try:
            #the taglist
            if 'taglist' in request.POST:
                taglist = request.POST['taglist'].split(',')
                db.update_workflow(username,int(id),{},taglist)
    
        except db.NoSuchWorkflow, e:
            logger.critical('%s' % e)
            return HttpResponseNotFound(e)
            
        return HttpResponse("Success")
                                        
    elif request.method == 'GET':
        try:
            tags = db.get_tags_for_workflow(username,int(id))
    
        except (ObjectDoesNotExist, Exception), e:
            logger.critical('%s' % e)
            return HttpResponseNotFound(e)
            
        return HttpResponse(json.dumps(tags),
                                        mimetype='application/json')
                                        
    return HttpResponseServerError('Unsupported request method\n')


def workflow_id_tags_add(request, username, id=None):
    logger.debug('')
    db.ensure_user_db(username)
    
    if not id or not username:
        return HttpResponseNotFound('No id or no username supplied.\n')

    if request.method == 'POST': 
        try:
            #the taglist
            if 'taglist' in request.POST:
                taglist = request.POST['taglist'].split(',')
                db.tag_workflow(username,int(id),taglist)
    
        except db.NoSuchWorkflow, e:
            logger.critical('%s' % e)
            return HttpResponseNotFound(e)
            
        return HttpResponse("Success")
                                        
    return HttpResponseServerError('Unsupported request method\n')


def workflow_id_tags_remove(request, username, id=None):
    logger.debug('')
    db.ensure_user_db(username)
    
    if not id or not username:
        return HttpResponseNotFound('No id or no username supplied.\n')
    
    if request.method == 'POST': 
        try:
            #the taglist
            if 'taglist' in request.POST:
                taglist = request.POST['taglist'].split(',')
                db.detag_workflow(username,int(id),taglist)
        except db.NoSuchWorkflow, e:
            logger.critical('%s' % e)
            return HttpResponseNotFound(e)
        return HttpResponse("Success")
                                        
    return HttpResponseServerError('Unsupported request method\n')


def workflow_id_tags_search(request, username):
    logger.debug('')
    db.ensure_user_db(username)
    
    if not username:
        return HttpResponseNotFound('No username supplied.\n')
    
    if request.method == 'GET': 
        search = request.GET['keyword']
        operator = request.GET['operator'] if 'operator' in request.GET else 'LIKE'
        
        tags = db.find_tag_by_search(username,search,operator)
        
        return HttpResponse(json.dumps(tags), mimetype='application/json')

    return HttpResponseServerError('Unsupported request method\n')


def workflow_tag(request, username, tag):
    logger.debug('')
    db.ensure_user_db(username)
    
    if not tag or not username:
        return HttpResponseNotFound('No id or no username supplied.\n')
    
    if request.method == 'GET': 
        return HttpResponse(json.dumps(db.find_workflow_by_tag(username,tag)),mimetype='application/json')
    
    return HttpResponseServerError('Unsupported request method\n')


def workflow_all_tags(request, username):
    logger.debug('')
    db.ensure_user_db(username)
    
    if not username:
        return HttpResponseNotFound('No id or no username supplied.\n')
    
    if request.method == 'GET': 
        return HttpResponse(json.dumps(db.get_tags(username)),mimetype='application/json')
    
    return HttpResponseServerError('Unsupported request method\n')


def workflow_date_search(request, username):
    logger.debug('')
    db.ensure_user_db(username)
    if request.method == 'GET':
        start = request.GET['start']
        end = request.GET['end'] if 'end' in request.GET else 'now'
        sort = request.GET['sort'] if 'sort' in request.GET else 'created_on'
        
        workflows = db.find_workflow_by_date(username,start,end,sort)
        
        return HttpResponse(json.dumps(workflows), mimetype='application/json')
    
    return HttpResponseServerError('Unsupported request method\n')
    
    
def workflow_search(request, username):
    logger.debug('')
    db.ensure_user_db(username)
    if request.method == 'GET':
        search = request.GET['keyword']
        field = request.GET['field'] if 'field' in request.GET else 'name'
        sort = request.GET['sort'] if 'sort' in request.GET else 'created_on'
        operator = request.GET['operator'] if 'operator' in request.GET else 'LIKE'
        
        workflows = db.find_workflow_by_search(username,search,field,sort,operator)
        
        return HttpResponse(json.dumps(workflows), mimetype='application/json')
    
    return HttpResponseServerError('Unsupported request method\n')
    
