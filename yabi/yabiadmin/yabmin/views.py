from yabiadmin.yabmin.models import User, ToolGrouping, ToolGroup
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404

class ToolGroupView:
    def __init__(self, name):
        self.name = name
        self.tools = set([])

    def sorted_tools(self):
        for tool in sorted(self.tools):
            yield tool

def tools(request, user_id):
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

