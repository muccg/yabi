from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.db import connection
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from yabiadmin.yabmin.models import User, ToolGrouping, ToolGroup, Tool, ToolParameter
from yabiadmin import ldaputils
from django.utils import webhelpers
import simplejson as json
from json_util import makeJsonFriendly
from django.contrib.auth.decorators import login_required

class ToolGroupView:
    def __init__(self, name):
        self.name = name
        self.tools = set([])

    def sorted_tools(self):
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
        if tp.input_extensions.all():
            props.append('Input extensions: ' + ",".join(
                ['"%s"' % ie.extension for ie in tp.input_extensions.all()]))
        if tp.output_file:
            props.append('Output File')
        if tp.filter:
            filter_text = tp.filter.display_text
            if tp.filter_value:
                filter_text += ' "%s"' % tp.filter_value
            props.append(filter_text)
        if tp.source_param:
            props.append('Source parameter: ' + tp.source_param.switch)
        if tp.extension_param:
            props.append('Extension parameter: ' + tp.extension_param.switch)
        return props
        return props

def format_params(tool_parameters):
    for param in tool_parameters:        
        yield ToolParamView(param)

@staff_member_required
def tool(request, tool_id):
    tool = get_object_or_404(Tool, pk=tool_id)
    
    return render_to_response('yabmin/tool.html', {
                'tool': tool,
                'user':request.user,
                'title': 'Tool Details',
                'root_path':webhelpers.url("/admin"),
                'tool_params': format_params(tool.toolparameter_set.order_by('id')),
           })

@staff_member_required
def user_tools(request, user_id):
    tooluser = get_object_or_404(User, pk=user_id)
    tool_groupings = ToolGrouping.objects.filter(tool_set__users=tooluser)
    unique_tool_groups = {}
    for grouping in tool_groupings:
        tool_group_name = grouping.tool_group.name 
        tool_name = grouping.tool.name
        tgv = unique_tool_groups.setdefault(tool_group_name, ToolGroupView(tool_group_name))
        tgv.tools.add(tool_name)

    return render_to_response("yabmin/user_tools.html", {
        'user': request.user,
        'tooluser': tooluser,
        'title': 'Tool Listing',
        'root_path':webhelpers.url("/admin"),
        'tool_groups': sorted(unique_tool_groups.values(), key = lambda tgv: tgv.name)})

class LdapUser:
    def __init__(self, uid, dn, full_name):
        self.uid = uid
        self.dn = dn
        self.full_name = full_name

def format(dn, ldap_user):
    return LdapUser(ldap_user['uid'][0], dn, ldap_user['cn'][0])

def register_users(uids):
    for uid in uids:
        user = User(name=uid)
        user.save()

@staff_member_required
def ldap_users(request):
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
 
    return render_to_response("yabmin/ldap_users.html", {
                'unexisting_ldap_users': unexisting_ldap_users,
                'existing_ldap_users': existing_ldap_users
            })

def ws_tool(request, toolname):

    try:
        tool = Tool.objects.get(name=toolname)
        return HttpResponse(tool.json())
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Object not found")
