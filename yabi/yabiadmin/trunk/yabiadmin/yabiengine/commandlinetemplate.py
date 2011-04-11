# -*- coding: utf-8 -*-
import httplib, os
from urllib import urlencode

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import simplejson as json, webhelpers
from django.db.models.signals import post_save
from django.utils.webhelpers import url

from yabiadmin.yabi.models import Backend, BackendCredential, Tool, User
from yabiadmin.yabiengine import backendhelper
from yabiadmin.yabiengine.models import Workflow, Task, Job
from yabiadmin.yabiengine.urihelper import uriparse, url_join

import pickle

import logging
logger = logging.getLogger('yabiengine')

DEBUG = False

# Helper function to do basic command argument quoting.
def quote_argument(s):
    ESCAPE_CHARS = r'\"'
    for c in ESCAPE_CHARS:
        s = s.replace(c, "\\" + c)
    return '"' + s + '"'

class Arg(object):
    """An argument to the command line"""
    takes_input_file = False
    takes_output_file = False
    
    def __init__(self, arg):
        self.arg=arg
        
    def render(self):
        return self.arg

class SwitchFilename(object):
    """represents the filename that the render() was run with. It is at template time, unknown. It is filled in with render"""
    def __init__(self,default="unkown",template="%s"):
        self.filename = default
        self.template = template
        
    def __str__(self):
        """This is the render function that renders the filename"""
        return quote_argument(self.template%self.filename)
        
    def set(self, filename):
        self.filename = filename

class Switch(Arg):
    """A flag for a command with an optional parameter"""
    
    def __init__(self,flag,value=None, switchuse=None):
        self.flag=flag
        self.value=value
        
        self.switchuse=switchuse                 # comes from the switch use entry of the tool param (example: "%(switch)s %(value)s"

        self.takes_output_file = not (type(value) is str or type(value) is unicode)

    def as_string(self):
        assert self.switchuse is not None, "Switch 'switchuse' has not been set"
        assert type(self.switchuse) is str or type(self.switchuse) is unicode, "Switch 'switchuse' is wrong type"
        return self.switchuse%{'switch':self.flag, 'value':self.value}
        
    def __str__(self):
        return "<switch:%s value:%s>"%(self.flag, self.value)
        
    def __repr__(self):
        return str(self)
        
    def render(self,output=None):
        if output:
            self.value.set(output)
        return self.as_string()
       
class BatchSwitch(Switch):
    """This represents a batch file switch that knows it needs a batch filename at some future point"""
    takes_input_file = True
    
    def __str__(self):
        return "<batchswitch:%s value:%s>"%(self.flag, self.value)
    
    def render(self, filename):
        assert self.switchuse is not None, "Switch 'switchuse' has not been set"
        assert type(self.switchuse) is str or type(self.switchuse) is unicode, "Switch 'switchuse' is wrong type"
        return self.switchuse%{'switch':self.flag, 'value':quote_argument(filename)}
    
class BatchArg(Arg):
    """This represents a batch file argument that knows it needs a batch filename at some future point"""
    def __str__(self):
        return "<batcharg:%s>"%(self.arg)
        
class Command(object):
    """A path to a command"""
    is_select_file = False
    
    def __init__(self, path):
        self.path = path
        
    def __str__(self):
        return "<command: %s>"%self.path
        
    def render(self):
        return self.path
        
class SelectFile(Command):
    is_select_file = True
    
    def __init__(self):
        pass
    
    def __str__(self):
        return "<select file>"
        
    def render(self):
        return ""
    
class CommandTemplate(object):
    """Holds the structure of a yabi command including the associated flags and arguments
    
    To use CommandTemplate you do the following.
    
    * create a CT
    
        template = CommandTemplate()
        
    * create the template from a job and job descriptor dictionary
    
        template.setup( job, job_dict )
        template.parse_parameter_description()
        
       this initialises the command template structure according to the incoming job.
       
    * serialise and deserialise the object
    
        data = template.serialise()
        template.deserialise(data)
        
    
    The command template hold onto the backreferences to previous jobs. For this reason after other jobs in the workflow
    finish you need to update the command templates file links. To do this you have the following:
    
    * update the backrefs and convert any finished pre-jobs into file links. Pass in the django workflow object associated with this job
    
        template.update_dependencies(workflow)
    
    * to test if this job still has any left over dependencies
    
        if template.dependencies == 0:
            # ready to run
            job.ready()
            
            
    Once you are ready to create tasks from a command template:
    
    * set the conversion template string that will convert a URI to a local file path
        
        template.set_uri_conversion("/some/long/remote/path/to/%(filename)s")
    
    * render the final command line passing batch file URIs in. TODO: support passing in more than one batch file
    
        command = template.render( batch_file1 )
        
    * once render is called, this template object becomes an expression of that task. Get all the stagein files (including the batch files and parameter files and others:
        
        for uri in template.all_files():
            # add stage in uri to task
            task.add_stagein_uri(uri)
            
    * alternatively once render()ed you can get back just the batch files you passed in, or just the other non-batch files
    
        batch_files = template.batch_files()
        other_files = template.other_files()
       
    """
    
    def __init__(self):
        """Initialise a blank command template"""
        # build lists of filenames here
        self.arguments = []                 # a list of our flags, parameters and arguments
        self.files = []                     # a list of any extra 'input files' required. The items are dictionaries that are copies of the "parameter" input dictionary describing the selection
        self.backrefs = []                  # a list of any previous jobs we are waiting on
        self.batchfiles = []                # once a previous job is finished, the files that are represented by the output of that job for use by us are assembled here
                                            # these are the URIs that are converted to the final /full/directory/path to use in the command
        self.backfiles = []                 # when the backrefs are processed, this array is filled with the decoded reference URIs. this is to be used by the caller to be passed back into render
                                            # this represents ALL the possibilities that could be batched, not _just_ those relating to render()
 
        self.uri_conversion_string = "%%(file)s"            # to convert a URI into a remote path we use this string template
 
    def setup(self, job, job_dict):
        """
        setup the command template as per the job passed in and the parameter dictionary passed in
        """
        # input
        self.job = job
        self.job_dict = job_dict
        
        # we need username for backend FS calls
        self.username = self.job.workflow.user.name
            
        # make sure jobId on the json is always one greater than the workflow id
        assert self.job.order == job_dict["jobId"] - 1
            
        toolname = job_dict["toolName"]
        parameters = job_dict["parameterList"]["parameter"]
        tool = self.tool = Tool.objects.get(name=toolname)
        
        if not tool.path:
            # we are a "select file" tool
            self.command=SelectFile()
        else:
            # we are a normal command
            self.command=Command(tool.path)
        
        # pack incoming params into dictionary
        self.params = dict( [(p['switchName'],p) for p in parameters] )
            
    def dump(self):
        print "%s (%s)"%(str(self.command),str(self.arguments))
        
    def serialise(self):
        import pickle
        return pickle.dumps([self.command,self.arguments,self.files,self.backrefs,self.username,self.backfiles,self.batchfiles])

    def deserialise(self, data):
        self.command, self.arguments,self.files,self.backrefs,self.username,self.backfiles,self.batchfiles = pickle.loads(str(data))

    def set_uri_conversion(self, string):
        self.uri_conversion_string = string

    def _convert(self, uri):
        """convert a uri into a full remote path"""
        schema,rest = uriparse(uri)
        return self.uri_conversion_string%{     
            'schema':schema,
            'hostname':rest.hostname,
            'username':rest.username,
            'port':rest.port,
            'fullpath':rest.path,
            'filename':rest.path.rsplit("/",1)[-1]
        }

    def render(self, *batchfiles):
        # ATM only one file per batch
        self.batchfiles = batchfiles
        batchfiles = list(batchfiles)
        assert len(self.batchfiles)<=1

        # our 'output filename base' is just the filename of the first batchfile (ATM)
        if batchfiles:
            output_filename = batchfiles[0].rsplit("/")[-1]

        output = self.command.render()
        
        for argument in self.arguments:
            if argument.takes_input_file:
                assert len(batchfiles), "batch_files passed in has %d entries which is not enough for command tempate %r"%(len(self.batchfiles),self)
                output += " "+argument.render(self._convert(batchfiles.pop(0)))
            elif argument.takes_output_file:
                output += " "+argument.render(output_filename)
            else:
                output += " "+argument.render()
            
        return output
        
    def parse_parameter_description(self):
        """Parse the json parameter description"""
        tool = self.tool
        
        # loop over each of the tools parameters
        for tp in tool.toolparameter_set.order_by('rank').all():
            # check the tool switch against the incoming params
            if tp.switch not in self.params:
                logger.debug("Switch ignored [%s]" % tp.switch)
                continue

            if DEBUG:
                print "TP->%s"%tp.switch  
                print "self.params[%s]=%s"%(tp.switch,self.params[tp.switch])
            
            # check to see if the param description refers to a filesystem
            params = self.params[tp.switch]
            if params['valid']:
                details = params['value']
                for value in details:
                    if 'type' in value and (value['type']=='file' or value['type']=='directory'):
                        # param refers to a file
                        assert tp.input_file, "File parameter passed in on switch '%s' where the input_file table boolean is not set"%(tp.switch)
                        value['extensions'] = tp.input_filetype_extensions()
                        self.files.append(value)
                    else:
                        # switch has single parameter
                        if DEBUG:
                            if tool.batch_on_param_bundle_files:
                                print "!!!![%s] tool.batch_on_param_bundle_files"%(tp.switch)
                            if tp.input_file:
                                print "!!!![%s] tp.input_file"%(tp.switch)
                            if tp.output_file:
                                print "!!!![%s] tp.output_file"%(tp.switch)
                            if tp.use_batch_filename:
                                print "!!!![%s] tp.use_batch_filename"%(tp.switch)
                            if tp.extension_param:
                                print "!!!![%s] tp.extension_param"%(tp.switch)
                        if type(value) is dict:
                            assert "type" in value and (value['type']=='job' or value['type']=='jobfile'), "Unknown param value type for switch '%s', type is '%s'"%(tp.switch,value['type'])           # TODO: support type 'jobfile' correctly
                            
                            # annotate extra info
                            value['extensions'] = tp.input_filetype_extensions() 
                            value['bundle_extra_files'] = tool.batch_on_param_bundle_files
                    
                            # save the param
                            self.backrefs.append(value)       
                            assert tp == tool.batch_on_param
                            
                            self.arguments.append( BatchSwitch( tp.switch, switchuse=tp.switch_use.formatstring ) )
                            
                        elif type(value) is str or type(value) is unicode:
                            value = quote_argument( value )
                            
                            if tp.output_file:
                                if tp.use_batch_filename:
                                    if tp.extension_param:
                                        value = SwitchFilename(default=value, template="%s."+str(tp.extension_param))
                                    else:
                                        value = SwitchFilename(default=value)
                                
                            self.arguments.append( Switch( tp.switch, value, switchuse=tp.switch_use.formatstring ) )
    
    def get_dependencies(self):
        # at this point, some of the backrefs may have resolved themselves
        # we should update the backrefs to reflect the new state
        return len(self.backrefs)
    dependencies = property(get_dependencies)
    
    def update_dependencies(self,workflow):
        new_backrefs=[]
        for backref in self.backrefs:
            assert 'type' in backref and (backref['type']=="job" or backref['type']=='jobfile')                     # TODO: support jobfile correctly
            job_index = backref['jobId']-1
            
            # get this job
            job = workflow.get_job(job_index)
            stageout = job.stageout
            file_list = backendhelper.get_file_list(self.username, stageout)
            
            # has the job finished?
            if job.status == "complete":
                # do we now have files for this old job?
                if len(file_list):
                    for filename, size, date, link in file_list:
                        details = {
                                "path" : [],
                                "filename" : filename,
                                "type" : "file",
                                "root" : stageout,
                                "pathComponents" : [ stageout ],
                                "extensions" : backref['extensions']
                            }
                        self.backfiles.append(details)
                        
                        if backref['bundle_extra_files']:
                            # this file should be forced into the file list
                            self.files.append(details)
                else:
                    # job is finished but there are no files created!
                    assert job.status=="error"
                    new_backrefs.append(backref)
                        
            else:
                # job still hasnt finished
                new_backrefs.append(backref)
            
                
        self.backrefs=new_backrefs
        
    def other_files(self):
        """Look through the command and compile a list of file uri's that need to be 'aquired' by the stagein process"""
        for selection in self.files:
            for file in self.parse_param_value(selection):
                yield file
        
    def batch_files(self):
        """Like stageins but only those files assosicated with this rendering instance of the template as batch files
        Returns remote fs paths, not URIs
        """
        for selection in self.batchfiles:
            yield selection
            
    def all_files(self):
        for file in self.other_files():
            yield file
            
        for file in self.batch_files():
            yield file
            
    def all_possible_batch_files(self):
        """This returns all possible input batch files for this command template. Not just those used by this render.
        This generator is used to return all the possibilities for batch. From this we call render on each one to derive a task
        """
        for selection in self.backfiles:
            for file in self.parse_param_value(selection):
                yield file, selection['extensions']
    
    def parse_param_value(self,item):
        if item['type'] == 'file':
            # decode file params
            return [self.parse_param_file_value(item)]
                
        elif item['type'] == 'directory':
            # decode directory
            return [file for file in self.parse_param_directory_value(item)]
    
    def parse_param_file_value(self, item):
        path = ''
        if item['path']:
            path = os.path.join(*item['path'])
            if not path.endswith(os.sep):
                    path = path + os.sep
        return '%s%s%s' % (item['root'], path, item['filename'])
        
    def parse_param_directory_value(self, item):
        fulluri = item['root']+item['filename']+'/'

        # get recursive directory listing
        filelist = backendhelper.get_file_list(self.username, fulluri, recurse=True)
        return [ fulluri + X[0] for X in filelist ] 
     