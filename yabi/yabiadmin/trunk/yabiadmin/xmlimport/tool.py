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
"""
Import a Tool definition from a baat XML file into the DB.

Invoke import_tool(filename) to import one file at a time.
To import all files from a directory look at the functions defined
at the module level. 
Django's ORM is used to save the entities to the DB, so the easiest
way to run the import is from a Django shell (ie. ./manage.py shell or
./manage.py shell_plus if you have Django extensions installed).
The Tool and the related entitites are saved in one transaction, on any
error the transaction is rolled back.
"""
import glob, os, sys
from xml.dom.minidom import parse

from yabiadmin.yabi.models import *
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

def import_tool(filename):
    """Import a tool from the given baat XML file."""
    doc = parse(filename)
    job_element_container = doc.getElementsByTagName('job')
    assert job_element_container, \
           "Couldn't find required element 'job' in the XML file %s." % filename
    job_element = job_element_container[0]
    
    tool_name = os.path.splitext(os.path.basename(filename))[0]
    tool = Tool()
    populate_simple_fields(tool, job_element)
    validate_simple_fields(tool, tool_name)
    populate_rest_and_save(tool, job_element)

# Implementation

def populate_simple_fields(tool, job_element):
    props_from_attrs(tool, job_element, 
                     name='toolName', path='toolPath', 
                     display_name='displayName', description='description')

    # add all tools with null backend by default, user can then select backend from admin
    backend = Backend.objects.get(name="nullbackend")
    tool.backend = backend
    tool.fs_backend = backend

def validate_simple_fields(tool, tool_name):
    assert tool_name == tool.name, ("Inconsistent tool name. " 
                "Filename is '%s' but job.toolName is '%s'" 
                % (tool_name, tool.name))
    assert not Tool.objects.filter(name=tool_name), \
                "Tool named '%s' already exists" % tool_name

@transaction.commit_on_success
def populate_rest_and_save(tool, job_element):
    """Save the tool and all related entities in one transaction."""
    tool.save()
    input_filetypes = extract_input_filetypes(job_element)
    extract_and_save_toolparams(tool, input_filetypes, job_element)
    extract_batch_props(tool, job_element)
    extract_output_filetypes(tool, job_element)
    tool.save()

def extract_and_save_toolparams(tool, input_filetypes, job_element):
    self_refs = {}
    for paramlist in job_element.getElementsByTagName('parameterList'):
        for param_element in paramlist.getElementsByTagName('parameter'):
            tool_param = tool_param_from_xml(param_element) 
            tool.toolparameter_set.add(tool_param)
            if tool_param.input_file:
                add_input_filetypes(param_element, tool_param, input_filetypes)
            self_refs[tool_param] = param_self_refs(param_element, tool)
    save_toolparam_self_refs(tool, self_refs)

def save_toolparam_self_refs(tool, references):
    for (child_param, refs) in references.iteritems():
        for (prop, parent_switchname) in refs.iteritems():
            parent_param = tool.toolparameter_set.all().get(switch=parent_switchname)
            setattr(child_param, prop, parent_param) 
        child_param.save()

def extract_batch_props(tool, job_element):
    for batch_element in job_element.getElementsByTagName('batchOnParameter'):
        param_name = attribute_value(batch_element, 'name')
        tool.batch_on_param = tool.toolparameter_set.get(switch=param_name)
        tool.batch_on_param_bundle_files = attribute_value(batch_element, 'bundleFiles') == "true"

def extract_output_filetypes(tool, job_element):
    for outfiletype_element in job_element.getElementsByTagName('outputFiletypes'):
        tool.file_pass_thru = to_bool(attribute_value(outfiletype_element, 'filePassThru'))
        for extension_element in outfiletype_element.getElementsByTagName('extension'):
            extension = extract_output_extension(tool, extension_element)
            tool.tooloutputextension_set.add(extension)

def extract_output_extension(tool, extension_element):
    extension = ToolOutputExtension()
    extension_name = extension_element.firstChild.data
    extension.file_extension = get_or_create_refdata(
            FileExtension, extension_name, field='extension')
    extension.must_exist = to_bool(
            attribute_value(extension_element, 'mustExist'))
    extension.must_be_larger_than = to_int(
            attribute_value(extension_element, 'mustBeLargerThan'))
    return extension
 
def extract_input_filetypes(job_element):
    all_filetypes = []
    for file_types in job_element.getElementsByTagName('inputFiletypes'):
        for extension in [ ext_elem.firstChild.data 
                for ext_elem in file_types.getElementsByTagName('extension')]:
            file_ext = get_or_create_refdata(FileExtension, extension, field='extension')
            file_type = get_or_create_file_type_for_extension(file_ext)
            all_filetypes.append(file_type)
    return all_filetypes

def get_or_create_file_type_for_extension(file_ext):
    for file_type in file_ext.filetype_set.all():
        # file type has this and only this file extension
        if len(file_type.extensions.all()) == 1:
            return file_type
    return file_ext.filetype_set.create(
                    name = file_ext.extension + " (GEN)")

def param_self_refs(param_element, tool):
    references = {}
    source_param_name = attribute_value(param_element, 'sourceParam')
    if source_param_name:
        references['source_param'] = source_param_name
    extension_param_name = attribute_value(param_element, 'extensionParam')
    if extension_param_name:
        references['extension_param'] = extension_param_name
    return references

def tool_param_from_xml(param_element):
    tool_param = ToolParameter()
    tool_param.rank = to_int(attribute_value(param_element, 'rank'))
    tool_param.mandatory = to_bool(attribute_value(param_element, 'mandatory'))
    tool_param.input_file = to_bool(attribute_value(param_element, 'inputFile'))
    tool_param.output_file = to_bool(attribute_value(param_element, 'outputFile'), False)
    tool_param.switch = attribute_value(param_element, 'switch')

    switch_use_name = attribute_value(param_element, 'switchUse')
    if switch_use_name:
        try:
            tool_param.switch_use = ParameterSwitchUse.objects.get(display_text=switch_use_name)
        except ObjectDoesNotExist:
            pass

    tool_param.default_value = attribute_value(param_element, 'value')

    return tool_param

def add_input_filetypes(param_element, tool_param, default_input_filetypes):
    accepted_extensions = []
    for ext_list in param_element.getElementsByTagName('acceptedExtensionList'):
        for ext in ext_list.getElementsByTagName('acceptedExtension'):
            accepted_extensions.append(ext.firstChild.data)
    if accepted_extensions:
        for extension_name in accepted_extensions:
            file_ext = get_or_create_refdata(FileExtension, extension_name, field='extension')
            file_type = get_or_create_file_type_for_extension(file_ext)
            tool_param.accepted_filetypes.add(file_type)
    else:
        for file_type in default_input_filetypes:
            tool_param.accepted_filetypes.add(file_type)

def get_or_create_refdata(reftype, value, field='name'):
    kw = {field: value}
    reference_container = reftype.objects.filter(**kw)
    if reference_container:
        refdata = reference_container[0] 
    else:
        refdata = reftype(**kw)
        refdata.save()
    return refdata

def attribute_value(xml_element, attribute):
    if xml_element.hasAttribute(attribute):
        return xml_element.attributes[attribute].nodeValue

def props_from_attrs(obj, xml_element, **kwargs):
    for (prop, value) in [ (prop, attribute_value(xml_element, attr)) 
                           for (prop,attr) in kwargs.iteritems() ]:
        if value and not value.strip() == "":
            setattr(obj, prop, value)

def to_bool(str_value,default=None):
    if str_value is not None:
        return str_value.lower() in ("yes", "true")
    return default

def to_int(str_value):
    if not (str_value is None or str_value.strip() == ""):
        return int(str_value)

if __name__ == '__main__':
    import_tool(sys.argv[1])

