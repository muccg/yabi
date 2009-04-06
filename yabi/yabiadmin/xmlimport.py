import os
import sys
from xml.dom.minidom import parse
from yabiadmin.yabmin.models import Tool, ToolRslInfo

def _find_associated_tool(filename):
    tool_name = os.path.splitext(os.path.basename(filename))[0]
    tools = Tool.objects.filter(name=tool_name)
    if tools:
        return tools[0]

def _get_value(root_elem, element_name):
    element = root_elem.getElementsByTagName(element_name)[0]
    return element.firstChild.data

def _populate_rsl_info_fields(rsl_info, root_elem):
    rsl_info.executable = _get_value(root_elem, 'executable')
    rsl_info.count = _get_value(root_elem, 'count')
    rsl_info.queue = _get_value(root_elem, 'queue')
    rsl_info.max_wall_time = _get_value(root_elem, 'maxWallTime')
    rsl_info.max_memory = _get_value(root_elem, 'maxMemory')
    rsl_info.job_type = _get_value(root_elem, 'jobType')

def _extract_argument_orders(root_elem):
    position = "before arguments"
    arguments = []
    for child in root_elem.childNodes:
        if position == "before arguments":
            if child.nodeName not in ('argument', 'argumentPlaceholder'):
                continue
            position = "in arguments"
        if position == "in arguments":
            if child.nodeName not in ('argument', 'argumentPlaceholder'):
                break
            if child.nodeName == 'argumentPlaceholder':
                arguments.append('ALL')
            else:
                arguments.append(child.firstChild.data)
    return arguments or ['ALL']

def _extract_extension_modules(root_elem):
    modules = []
    for extension_elem in root_elem.getElementsByTagName("extensions"):
        for module in extension_elem.getElementsByTagName("module"):
            modules.append(module.firstChild.data)
    return modules

def _save_argument_orders(rsl_info, args):
    for i, arg in enumerate(args):
        rsl_info.toolrslargumentorder_set.create(name=arg,rank=i+1)

def _save_extension_modules(rsl_info, modules):
    for module in modules:
        rsl_info.toolrslextensionmodule_set.create(name=module)

def import_rsl(filename):
    tool = _find_associated_tool(filename)
    assert tool, "Couldn't find tool for filename %s. Can't proceed!" % filename
    rsl_infos = ToolRslInfo.objects.filter(tool=tool)
    assert not rsl_infos, "A tool rsl info for tool (%d: %s) already exists." \
                           % (tool.id, tool.name) + "Can't proceed!"

    doc = parse(filename)
    root_elem = doc.firstChild
    assert root_elem.nodeName == "job", 'The root element should be called "job"'

    rsl_info = ToolRslInfo(tool=tool)
    _populate_rsl_info_fields(rsl_info, root_elem)
    args = _extract_argument_orders(root_elem)
    modules = _extract_extension_modules(root_elem)

    rsl_info.save()
    _save_argument_orders(rsl_info, args)
    _save_extension_modules(rsl_info, modules)

if __name__ == '__main__':
    import_rsl(sys.argv[1])

