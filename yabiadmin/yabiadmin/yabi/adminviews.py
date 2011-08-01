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
import sys
from urllib import quote
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.db import connection
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.core import urlresolvers
from yabiadmin.yabi.models import *
from yabiadmin import ldaputils
from django.utils import webhelpers
from django.utils import simplejson as json
from json_util import makeJsonFriendly
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django import forms
from django.forms.util import ErrorList

import logging
logger = logging.getLogger('yabiadmin')


class AddToolForm(forms.Form):
    tool_json = forms.CharField(widget=forms.Textarea)

    def clean_tool_json(self):
        data = self.cleaned_data['tool_json']
        try:
            tool_dict = json.loads(data)
        except Exception, e:
            raise forms.ValidationError("Unable to load json. Please check it is valid.")


        if Tool.objects.filter(name=tool_dict["tool"]["name"]):
            raise forms.ValidationError("A tool named %s already exists." % tool_dict["tool"]["name"])
        
        return data


class ToolGroupView:
    def __init__(self, name):
        self.name = name
        self.tools = set([])

    def sorted_tools(self):
        logger.debug('')        
        for tool in sorted(self.tools):
            yield tool

class ToolParamView:
    def __init__(self, tool_param):
        self._tool_param = tool_param
        self.rank = tool_param.rank is None and ' ' or tool_param.rank
        self.switch = tool_param.switch
        self.switch_use = tool_param.switch_use.display_text
        self.properties = self.other_properties()
        
    def other_properties(self):
        tp = self._tool_param
        props = []
        
        if tp.mandatory:
            props.append('Mandatory')
        if tp.input_file:
            props.append('Input File (%s)' % ",".join(
                ['"%s"' % af.name for af in tp.accepted_filetypes.all()]))
        if tp.output_file:
            props.append('Output File')
        if tp.use_output_filename:
            props.append('Use Output Filename: %s' % tp.use_output_filename)
        if tp.extension_param:
            props.append('Extension parameter: %s' % tp.extension_param.extension)
        if tp.batch_bundle_files:
            props.append('Bundle Files: %s' % tp.batch_bundle_files)

        return props
        return props

def format_params(tool_parameters):
    logger.debug('')
    for param in tool_parameters:        
        yield ToolParamView(param)

@staff_member_required
def tool(request, tool_id):
    logger.debug("")

    tool = get_object_or_404(Tool, pk=tool_id)
    
    return render_to_response('yabi/tool.html', {
        'tool': tool,
        'user':request.user,
        'title': 'Tool Details',
        'root_path':urlresolvers.reverse('admin:index'),
        'edit_url': urlresolvers.reverse('admin:yabi_tool_change', args=(tool.id,)),
        'json_url': webhelpers.url('/ws/tool/' + quote(tool.name)),
        'tool_params': format_params(tool.toolparameter_set.order_by('id')),
        })


@staff_member_required
def user_tools(request, user_id):
    logger.debug('')
    tooluser = get_object_or_404(User, pk=user_id)
    tool_groupings = ToolGrouping.objects.filter(tool_set__users=tooluser)
    unique_tool_groups = {}
    for grouping in tool_groupings:
        tool_group_name = grouping.tool_group.name 
        tool_name = grouping.tool.name
        tgv = unique_tool_groups.setdefault(tool_group_name, ToolGroupView(tool_group_name))
        tgv.tools.add(tool_name)

    return render_to_response("yabi/user_tools.html", {
        'user': request.user,
        'tooluser': tooluser,
        'title': 'Tool Listing',
        'root_path':urlresolvers.reverse('admin:index'),
        'tool_groups': sorted(unique_tool_groups.values(), key = lambda tgv: tgv.name)})

@staff_member_required
def user_backends(request, user_id):
    logger.debug('')
    backenduser = get_object_or_404(User, pk=user_id)

    becs = BackendCredential.objects.filter(credential__user=backenduser)

    return render_to_response("yabi/user_backends.html", {
        'user': request.user,
        'backenduser': backenduser,
        'title': 'Backend Listing',
        'root_path':urlresolvers.reverse('admin:index'),
        'backendcredentials': becs
        })

class LdapUser:
    def __init__(self, uid, dn, full_name):
        logger.debug('')
        self.uid = uid
        self.dn = dn
        self.full_name = full_name

def format(dn, ldap_user):
    logger.debug('')
    return LdapUser(ldap_user['uid'][0], dn, ldap_user['cn'][0])

def register_users(uids):
    logger.debug('')
    for uid in uids:
        user = User(name=uid)
        user.save()

@staff_member_required
def ldap_users(request):
    logger.debug('')
    if request.method == 'POST':
        register_users(request.POST.keys())

    all_ldap_users = ldaputils.get_all_users()
    yabi_userids = ldaputils.get_yabi_userids()

    ldap_yabi_users = [format(entry[0],entry[1]) for entry in 
            all_ldap_users.items() if entry[0] in yabi_userids ]
    
    db_user_names = [user.name for user in User.objects.all()]
    user_in_db = lambda u: u.uid in db_user_names

    existing_ldap_users = [user for user in ldap_yabi_users if user_in_db(user) ]
    unexisting_ldap_users = [user for user in ldap_yabi_users if not user_in_db(user) ]
 
    return render_to_response("yabi/ldap_users.html", {
        'unexisting_ldap_users': unexisting_ldap_users,
        'existing_ldap_users': existing_ldap_users,
        'root_path':urlresolvers.reverse('admin:index'),
        })

@staff_member_required
def backend(request, backend_id):
    logger.debug('')
    backend = get_object_or_404(Backend, pk=backend_id)
        
    return render_to_response('yabi/backend.html', {
        'backend': backend,
        'user':request.user,
        'title': 'Backend Details',
        'root_path':urlresolvers.reverse('admin:index'),
        })


@staff_member_required
def backend_cred_test(request, backend_cred_id):
    logger.debug('')

    bec = get_object_or_404(BackendCredential, pk=backend_cred_id)

    from yabiadmin.yabiengine import backendhelper

    try:
        rawdata = backendhelper.get_listing(bec.credential.user.name, bec.homedir_uri)
        listing = json.loads(rawdata)
        error = None
    except ValueError, e:
        listing = None
        error = rawdata
        
    return render_to_response('yabi/backend_cred_test.html', {
        'bec': bec,
        'user':request.user,
        'title': 'Backend Credential Test',
        'root_path':urlresolvers.reverse('admin:index'),
        'listing':listing,
        'error':error
        })


@staff_member_required
def add_tool(request):

    if request.method == 'GET':
        return render_to_response('yabi/add.html',
                                  {'form':AddToolForm(),
                                   'user':request.user,
                                   'title': 'Add Tool',
                                   'root_path':urlresolvers.reverse('admin:index'),                                   
                                   'action_path': urlresolvers.reverse('add_tool_view'),
                                   'breadcrumb':'Add Tool'
                                   }
                                  )
    else:

        f = AddToolForm(request.POST)
        if not f.is_valid():
            return render_to_response('yabi/add.html',
                                      {'form': f,
                                       'user':request.user,
                                       'title': 'Add Tool',
                                       'root_path':urlresolvers.reverse('admin:index'),                                       
                                       'action_path': urlresolvers.reverse('add_tool_view'),
                                       'breadcrumb':'Add Tool'
                                       }
                                      )
    
        else:

            tool_dict = json.loads(f.cleaned_data["tool_json"])
            tool_dict = tool_dict["tool"]
            tool = create_tool(request, tool_dict)
            
            return HttpResponseRedirect(urlresolvers.reverse('admin:yabi_tool_change', args=(tool.id,)))


@staff_member_required
def create_tool(request, tool_dict):
    # try and get the backends
    try:
        backend = Backend.objects.get(name=tool_dict['backend'])
    except ObjectDoesNotExist,e:
        backend = Backend.objects.get(name='nullbackend')

    try:
        fs_backend = Backend.objects.get(name=tool_dict['fs_backend'])
    except ObjectDoesNotExist,e:
        fs_backend = Backend.objects.get(name='nullbackend')

    # create the tool
    tool = Tool(name=tool_dict["name"],
                display_name=tool_dict["display_name"],
                path=tool_dict["path"],
                description=tool_dict["description"],
                enabled=tool_dict["enabled"],
                backend=backend,
                fs_backend=fs_backend,
                accepts_input=tool_dict["accepts_input"],
                cpus=tool_dict["cpus"],
                walltime=tool_dict["walltime"],
                module=tool_dict["module"],
                queue=tool_dict["queue"],
                max_memory=tool_dict["max_memory"],
                job_type=tool_dict["job_type"]
                )
    tool.save()


    # add the output extensions
    for output_ext in tool_dict["outputExtensions"]:
        extension, created = FileExtension.objects.get_or_create(pattern=output_ext["file_extension__pattern"])
        tooloutputextension, created = ToolOutputExtension.objects.get_or_create(tool=tool,
                                                                        file_extension=extension,
                                                                        must_exist=output_ext["must_exist"],
                                                                        must_be_larger_than=output_ext["must_be_larger_than"])


    # add the tool parameters
    for parameter in tool_dict["parameter_list"]:

        switch_use, created = ParameterSwitchUse.objects.get_or_create(display_text=parameter["switch_use__display_text"],
                                                                       formatstring=parameter["switch_use__formatstring"],
                                                                       description=parameter["switch_use__description"])

        toolparameter = ToolParameter(tool=tool,
                                      rank=parameter["rank"],
                                      mandatory=parameter["mandatory"],
                                      input_file=parameter["input_file"],
                                      output_file=parameter["output_file"],
                                      default_value=parameter["default_value"],
                                      helptext=parameter["helptext"],
                                      switch=parameter["switch"],
                                      hidden=parameter["hidden"],
                                      batch_param=parameter["batch_param"],
                                      batch_bundle_files=parameter["batch_bundle_files"]
                                      )


        if parameter["switch_use__display_text"] and parameter["switch_use__formatstring"] and parameter["switch_use__description"]:
            switch_use, created = ParameterSwitchUse.objects.get_or_create(display_text=parameter["switch_use__display_text"],
                                                                           formatstring=parameter["switch_use__formatstring"],
                                                                           description=parameter["switch_use__description"])
        else:
            # default to use "both" tool switch
            switch_use = ParameterSwitchUse.objects.get(display_text='both')

        toolparameter.switch_use=switch_use
        toolparameter.save() # so we can add many-to-many on accepted_filetypes

        # for each of the accepted filetype extension glob patterns get all associated filetypes and add them to tool parameter
        for ext_glob in parameter["acceptedExtensionList"]:
            fileextensions = FileExtension.objects.filter(pattern=ext_glob)
            for fe in fileextensions:
                filetypes = fe.filetype_set.all()
                for ft in filetypes:
                    toolparameter.accepted_filetypes.add(ft)

        # input extensions
        # TODO need to decide how to handle these, they are not in the tool json

        if parameter["possible_values"]:
            toolparameter.possible_values=json.dumps(parameter["possible_values"])

        toolparameter.save()


    # we need to do this in a separate loop otherwise the param we want to refer to doesn't exist yet
    for parameter in tool_dict["parameter_list"]:

        # add use_output_filename
        if "use_output_filename__switch" in parameter:
            try:
                outputfilename_toolparameter = ToolParameter.objects.get(tool=tool, switch=parameter["use_output_filename__switch"])
                toolparameter = ToolParameter.objects.get(tool=tool, switch=parameter["switch"])
                toolparameter.use_output_filename=outputfilename_toolparameter
                toolparameter.save()                
            except ObjectDoesNotExist,e:
                logger.critical("Unable to add use_output_filename on parameter.use_output_filename field: %s" % e)

        # add extension param
        if "extension_param" in parameter:
            try:
                extension = FileExtension.objects.get(pattern=parameter["extension_param"])
                toolparameter = ToolParameter.objects.get(tool=tool, switch=parameter["switch"])
                toolparameter.extension_param=extension
                toolparameter.save()                
            except ObjectDoesNotExist,e:
                logger.critical("Unable to add extension on parameter.extension field: %s" % e)


    tool.save()
    return tool

from crypto import DecryptException

@login_required
def password_collection(request):

    if request.method == 'POST':
        # bail early if canceled
        if 'button' in request.POST and request.POST['button'] == "Cancel":
            message = "No changes made."
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(webhelpers.url("/admin/yabi/credential/?ids=%s" % (request.POST['ids'])))
        else:
            ids = [int(X) for X in request.POST.get('ids', '').split(',')]     
            action = request.POST.get('action',None)
            assert action=="encrypt" or action=="decrypt" or action=="cache", "action should be encrypt, decrypt or cache. Instead it is '%s'"%action
            
            # just check we have the correct verify if its there
            if action=="encrypt":
                if request.POST["password"] != request.POST["checkpassword"]:
                    request.user.message_set.create(message="Passwords entered did not match!")
                    return HttpResponseRedirect(webhelpers.url("/admin/yabi/credential/?ids=%s" % (request.POST['ids'])))
                        
            success, fail = 0,0
            for id in ids:
                cred = Credential.objects.get(id=id)
                if action=='decrypt' or action=='cache':
                    if not cred.encrypted:
                        fail += 1
                    else:
                        try:
                            if action=="decrypt":
                                cred.decrypt(key=request.POST["password"])
                                cred.save()
                                success += 1
                            else:                   # action == "cache"
                                cred.send_to_memcache(key=request.POST["password"])
                                success += 1
                                
                        except DecryptException, de:
                            # failed decrypt. not saved.
                            fail += 1
                else:
                    cred.encrypt(key=request.POST["password"])
                    cred.save()

            if success:
                if success == 1:
                    message_bit = "1 credential %sed. " % action
                else:
                    message_bit = "%d credentials %sed. " % (success, action)
            else:
                message_bit = ""
                
            if fail:
                if fail == 1:
                    message_bit += "1 credential <b>failed</b> %sion." % action
                else:
                    message_bit += "%d credentials <b>failed</b> %sion." % (fail, action)
            
            if success or fail:
                request.user.message_set.create(message=message_bit)
            
            return HttpResponseRedirect(webhelpers.url("/admin/yabi/credential/?ids=%s" % (request.POST['ids'])))

    else:
        action = request.GET.get('action',None)
        assert action=="encrypt" or action=="decrypt" or action=="cache"
        ids = request.GET.get('ids', [])

        render_data = {'h':webhelpers,
                       #'ct': request.GET['ct'],
                       'return_url': '/varietydetail/',
                       'ids':ids,
                       'request':request,
                       'LANGUAGE_CODE':"en",
                       'title': "%s Credential"%(action.capitalize()),
                       'user':request.user,
                       'root_path':webhelpers.url("/"),
                       'action':action,
                       'plural':'s',
                       'checkpassword': action=="encrypt"
                       }

        return render_to_response('yabi/crypt_password.html', render_data)


@staff_member_required
def test_exception(request):
    raise Exception('Test exception')

