# -*- coding: utf-8 -*-

import copy

from django.http import HttpResponse
from yabiadmin.yabi import models
from django.utils import simplejson as json

from yabiadmin.yabistoreapp import db
from yabiadmin.yabiengine.tasks import build
from yabiadmin.yabiengine.enginemodels import EngineWorkflow

from yabiadmin.decorators import memcache, authentication_required

import logging
logger = logging.getLogger('yabiadmin')

class YabiError(StandardError):
    pass

class ParsingError(YabiError):
    pass

@authentication_required
def submitjob(request):
    logger.debug(request.user.username)

    # TODO extract common code from here and submitworkflow

    try:
        job = create_job(request)
        workflow_dict = create_wrapper_workflow(job)
        workflow_json = json.dumps(workflow_dict)
        user = models.User.objects.get(name=request.user.username)

        workflow = EngineWorkflow(name=workflow_dict["name"], user=user)
        workflow.save()

        # put the workflow in the store
        db.save_workflow(user.name, workflow.workflow_id, workflow_json, workflow.status, workflow.name)
    
        # trigger a build via celery
        build.delay(workflow_id=workflow.id)

        resp = {'success': True, 'workflow_id':workflow.id}
    except YabiError, e:
        resp = {'success': False, 'msg': str(e)}

    return HttpResponse(json.dumps(resp))

# Implementation

class ParamDef(object):
    def __init__(self, name, switch_use, mandatory):
        self.name = name
        self.switch_use = switch_use
        self.mandatory = mandatory
        self.value = None

    def matches(self, argument):
        if self.name == argument:
            return True
        if self.switch_use in ('combined', 'combined with equals'):
            if arguments.startswith(self.switch_use):
                value_start = len(self.name)
                if self.switch_use == 'combined with equals':
                    value_start += 1
                self.value = [argument[value_start:]]
                return True
        return False 

    def consume_values(self, arguments):
        '''WARNING! This changes the passed in arguments list in place! '''
        if self.switch_use == 'switchOnly':
            self.value = ['Yes']
            return 
        if self.switch_use == 'pair':
            if len(arguments) <= 1:
                raise ParsingError('Option %s requires 2 arguments' % self.name)
            v1 = arguments.pop(0)
            v2 = arguments.pop(0)
            if v1.startswith('-') or v2.startswith('-'):
                raise ParsingError('Option %s requires 2 arguments' % self.name)
            self.value = [v1, v2]

        if self.switch_use not in ('combined', 'combined_with_equals'):
            if not arguments:
                raise ParsingError('Option %s requires an argument' % self.name)
            v = arguments.pop(0)
            if v.startswith('-'):
                raise ParsingError('Option %s requires an argument' % self.name)
            self.value = [v]
 
    def switch_and_value(self):
        return [self.name, self.value] 

class YabiArgumentParser(object):
    def __init__(self, tool):
        self.paramdefs = self.init_paramdefs(tool)
        self.positional_paramdefs = filter(lambda x: x.switch_use == 'valueOnly', self.paramdefs)       

    def parse_args(self, arguments):
        arguments_copy = copy.copy(arguments) 
        parsed_options, unhandled_args = self.parse_options(arguments_copy)

        # Error if any unhandled argument are options (ie. start with '-' or '--')
        unknown_options = filter(lambda arg: arg.startswith('-'), [arg[0] for arg in unhandled_args])
        if unknown_options:
            raise ParsingError('Unknown option: %s' % ','.join(unknown_options))

        # All unhandled arguments have to be positional arguments
        if len(unhandled_args) != len(self.positional_paramdefs):
            pos_param_names = ', '.join([p.name for p in self.positional_paramdefs])
            raise ParsingError('Tool expects %d positional arguments (%s) but %d (%s) were passed in.' % 
                    ( len(self.positional_paramdefs), pos_param_names, 
                      len(unhandled_args), ', '.join([arg[0] for arg in unhandled_args])))

        parsed_positionals = self.parse_positionals([arg[0] for arg in unhandled_args])
        result = self.combine_results(parsed_options, parsed_positionals, unhandled_args)
        self.validate_mandatory(result)

        return result

    # Implementation

    def init_paramdefs(self, tool):
        return [ParamDef(param.switch, param.switch_use.display_text, param.mandatory) 
                    for param in tool.toolparameter_set.all()]

    def parse_options(self, arguments):
        remaining_args = arguments
        unhandled_args = []
        parsed_options = []

        last_arg = None
        while remaining_args:
            next_arg = remaining_args.pop(0)
            paramdef = self.find_matching_paramdef(next_arg)
            if paramdef:
                paramdef.consume_values(remaining_args)
                parsed_options.append(paramdef.switch_and_value()) 
            else:
                unhandled_args.append((next_arg, last_arg))
            last_arg = next_arg
        return parsed_options, unhandled_args

    def parse_positionals(self, unhandled_args):
        positionals = []
        for pos_paramdef in self.positional_paramdefs:
            pos_paramdef.consume_values(unhandled_args)
            positionals.append(pos_paramdef.switch_and_value())
        return positionals

    def combine_results(self, parsed_options, parsed_positionals, positional_order):
        # Start with the options ...
        result = copy.copy(parsed_options)
        # and insert the positionals at the right location based on the original order
        for positional in parsed_positionals:
            positional_value = positional[1][0]
            insert_after = find_item(positional_order, lambda x: x[0] == positional[1][0])[1]
            insert_idx = 0
            if insert_after is not None:
                insert_idx = item_index(result, lambda x: x[0] == insert_after) + 1
            result.insert(insert_idx, positional)
        return result

    def find_matching_paramdef(self, arg):
        for paramdef in self.paramdefs:
            if paramdef.matches(arg):
                return paramdef
            
    def validate_mandatory(self, result):
        mandatory_params = [p.name for p in self.paramdefs if p.mandatory]
        missing_params = [p for p in mandatory_params if p not in [arg[0] for arg in result]] 
        if missing_params:
            raise ParsingError('Mandatory option: %s not passed in.' % ','.join(missing_params))

def create_job(request):
    toolname = request.POST.get('name')
    tools = models.Tool.objects.filter(name=toolname)
    if len(tools) == 0:
        raise YabiError('Unknown tool name "%s"' % toolname)
    tool = tools[0]    
    argparser = YabiArgumentParser(tool)
    params = create_params(request, argparser)
    logger.debug('PARAMETER: ' + str(params))
    return {'toolName': tool.name, 'jobId': 1, 'valid': True, 
            'parameterList': {'parameter': params}}

def create_wrapper_workflow(job):
    def generate_name(job):
        return job['toolName']

    workflow = {
        'name': generate_name(job),
        # TODO this doesn't seem to be picked up
        'tags': ['yabish'],
        'jobs': [job]
    }
    
    return workflow    

def create_params(request, argparser):
    params = []
    arguments = reconstruct_argument_list(request)
    parsed_arguments = argparser.parse_args(arguments)

    return [{'switchName': arg, 'valid': True, 'value': value} 
                for arg,value in parsed_arguments]
    return params 

def reconstruct_argument_list(request):
    '''Reconstructs the argument list from request params named arg0, arg1, ... argN'''
    def argNtoN(argN):
        return int(argN[3:])
    arg_params = [(argNtoN(p[0]),p[1]) for p in request.POST.items() if p[0].startswith('arg')]
    arg_params.sort(cmp= lambda x,y: cmp(x[0],y[0]))
    arguments = [a[1] for a in arg_params]
    return arguments

def find_item(l, func):
    for item in l:
        if func(item):
            return item

def item_index(l, func):
    for i, item in enumerate(l):
        if func(item):
            return i

