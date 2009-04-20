from yabiadmin.yabmin.models import User, ToolGrouping, ToolGroup, Tool, ToolParameter
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.db import connection

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

def tool(request, tool_id):
    tool = get_object_or_404(Tool, pk=tool_id)
    
    return render_to_response('yabmin/tool.html', {
                'tool': tool, 
                'tool_params': format_params(tool.toolparameter_set.order_by('id')),
           })

def user_tools(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    tool_groupings = ToolGrouping.objects.filter(tool_set__users=user)
    unique_tool_groups = {}
    for grouping in tool_groupings:
        tool_group_name = grouping.tool_group.name 
        tool_name = grouping.tool.name
        tgv = unique_tool_groups.setdefault(tool_group_name, ToolGroupView(tool_group_name))
        tgv.tools.add(tool_name)

    return render_to_response("yabmin/user_tools.html", {
        'user': user,
        'tool_groups': sorted(unique_tool_groups.values(), key = lambda tgv: tgv.name)})

