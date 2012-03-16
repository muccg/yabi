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

import httplib, os
from urllib import urlencode

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import simplejson as json
from ccg.utils import webhelpers
from django.db.models.signals import post_save
from ccg.utils.webhelpers import url

from yabiadmin.yabi.models import Backend, BackendCredential, Tool, User
from yabiadmin.yabiengine import backendhelper
from yabiadmin.yabiengine.models import Workflow, Task, Job
from yabiadmin.yabiengine.urihelper import uriparse, url_join

import pickle
import fnmatch
import os.path

import logging
logger = logging.getLogger(__name__)

DEBUG = False

# Helper function to do basic command argument quoting.
def quote_argument(s):
    ESCAPE_CHARS = r'\"'
    for c in ESCAPE_CHARS:
        s = s.replace(c, "\\" + c)
    return '"' + s + '"'

def levenshtein(a,b):
    """Calculates the Levenshtein distance between a and b."""
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]

def make_fname(fname, ext):
    if not ext or fname.endswith(".%s"%(ext)):
        return fname
    return "%s.%s"%(fname,ext)

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
    def __init__(self,default="unkown",template=None, source_switch=None, extension=None):
        """template is a fucntion to call with the filename, and the new filename is returned"""
        self.filename = default
        self.template = template
        self.extension = extension
        
        # source switch is the "-switch" to be used as the originator of the filename for this switch. It is a string
        # eg. our object may describe output switch "-o" and source_switch may be "-i" meaning that the name for the
        # -o flag must be derived from the filename associated with the -i flag.
        self.source_switch = source_switch
        
    def __str__(self):
        """This is the render function that renders the filename"""
        return quote_argument(self.template(self.filename, self.extension))
        
    def set(self, filename):
        self.filename = filename
        
class SwitchInputFilename(object):
    """represents an input filename known at build time, but that will need to be converted at template render time. eg, a secondary input filename"""
    def __init__(self, filename):
        self.filename = filename
        self.convfunc = None
        
    def __str__(self):
        """Convert the filename using the conversion routine"""
        if self.convfunc:
            return quote_argument(self.convfunc(self.filename))
        else:
            return quote_argument(self.filename)
        
    def set(self, convfunc):
        """this is passed a conversion function to make the full filename"""
        assert callable(convfunc)
        self.convfunc = convfunc
        
class Switch(Arg):
    """A flag for a command with an optional parameter"""
    
    def __init__(self,flag,value=None, switchuse=None):
        self.flag=flag
        self.value=value
        
        self.switchuse=switchuse                 # comes from the switch use entry of the tool param (example: "%(switch)s %(value)s"

        # this flag is true if this switch needs to be given an output filename
        self.takes_output_file = not (type(value) is str or type(value) is unicode) and value.__class__ is SwitchFilename
        
        # this flag is true if this switch has a filename that needs to be converted to a fullpath at render time
        self.needs_filename_conversion = not (type(value) is str or type(value) is unicode) and value.__class__ is SwitchInputFilename

    def as_string(self):
        assert self.switchuse is not None, "Switch 'switchuse' has not been set"
        assert type(self.switchuse) is str or type(self.switchuse) is unicode, "Switch 'switchuse' is wrong type"
        return self.switchuse%{'switch':self.flag, 'value':self.value}
        
    def __str__(self):
        return "<Switch:%s Value:%s>"%(self.flag, self.value)
        
    def __repr__(self):
        return str(self)
        
    def render(self,output=None):
        if output:
            self.value.set(output)
        
        return self.as_string()
       
    @property
    def source_switch(self):
        return self.value.source_switch
       
class BatchSwitch(Switch):
    """This represents a batch file switch that knows it needs a batch filename at some future point"""
    takes_input_file = True
    
    def __str__(self):
        return "<BatchSwitch:%s Value:%s>"%(self.flag, self.value)
    
    def render(self, filenames):
        assert self.switchuse is not None, "Switch 'switchuse' has not been set"
        assert type(self.switchuse) is str or type(self.switchuse) is unicode, "Switch 'switchuse' is wrong type"
        assert len(filenames)==1, "BatchSwitch can only take single filenames"
        return self.switchuse%{'switch':self.flag, 'value':quote_argument(filenames[0])}
        
class ConsumerSwitch(BatchSwitch):
    """This represents a file input switch that doesn't 'batch' but instead tries to consume all the incoming files at once"""
    def __str__(self):
        return "<ConsumerSwitch:%s Value:%s>"%(self.flag, self.value)
    
    def render(self, filenames):
        assert self.switchuse is not None, "Switch 'switchuse' has not been set"
        assert type(self.switchuse) is str or type(self.switchuse) is unicode, "Switch 'switchuse' is wrong type"
        return self.switchuse%{'switch':self.flag, 'value':" ".join([quote_argument(X) for X in filenames])}

class UnknownFileSwitch(Switch):
    """This represents a non-batch file switch that doesn't know its filename but will find out at render time"""
    def __init__(self, *args, **kwargs):
        Switch.__init__(self, *args, **kwargs)
        self._resolved = False
        self.needs_filename_conversion = True
    
    def __str__(self):
        return "<UnknownFileSwitch:%s Value:%s resolved?:%s>"%(self.flag, self.value,str(self._resolved))
    
    def is_value(self, value):
        if self._resolved:
            return False            # resolved UnknownFileSwitches are never our backref value
    
        return self.value['type']==value['type'] and self.value['jobId']==value['jobId'] and self.value['extensions']==value['extensions']                    # TODO: IS this the best way to map UnknownFileSwitches with the backrefs?
    
    def is_value_resolved(self):
        return self._resolved
    
    def set_value(self, filename):
        self.value = filename
        self._resolved=True
    
    def render(self, convfunc):
        assert self.switchuse is not None, "Switch 'switchuse' has not been set"
        assert type(self.switchuse) is str or type(self.switchuse) is unicode, "Switch 'switchuse' is wrong type"
        
        # lets list the previous job files
        
        return self.switchuse%{'switch':self.flag, 'value':quote_argument(convfunc(self.value))}
    
class BatchArg(Arg):
    """This represents a batch file argument that knows it needs a batch filename at some future point"""
    def __str__(self):
        return "<BatchArg:%s>"%(self.arg)
        
class Command(object):
    """A path to a command"""
    is_select_file = False
    
    def __init__(self, path):
        self.path = path
        
    def __str__(self):
        return "<Command:%s>"%self.path
        
    def render(self):
        return self.path
        
class SelectFile(Command):
    is_select_file = True
    
    def __init__(self):
        pass
    
    def __str__(self):
        return "<SelectFile>"
        
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
    
    * render the final command line passing batch file URIs in.
    
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
        self.batchfiles = {}                # once a previous job is finished, the files that are represented by the output of that job for use by us are assembled here
                                            # these are the URIs that are converted to the final /full/directory/path to use in the command. the keys are the switch strings
                                            # the value the files.
        self.backfiles = {}                 # when the backrefs are processed, this array is filled with the decoded reference URIs. this is to be used by the caller to be passed back into render
                                            # this represents ALL the possibilities that could be batched, not _just_ those relating to render()
                                            # the keys here are the switch name. The value is a list of 'details'
 
        self.batch_switches = []            # the switches that need to have the input files batched
        self.consume_switches = []          # the switches that need to have the input files consumed
 
        self.uri_conversion_string = "%%(file)s"            # to convert a URI into a remote path we use this string template
        
    def setup(self, job, job_dict):
        """
        setup the command template as per the job passed in and the parameter dictionary passed in
        """
        if DEBUG:
            print "commandtemplate::setup(",job,",",job_dict,")"
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
        
        if DEBUG:
            print "params:",self.params
            
    def dump(self):
        print str(self)
        
    def __str__(self):
        return "%s (%s)"%(str(self.command),str(self.arguments))
        
    def serialise(self):
        import pickle
        return pickle.dumps([self.command,self.arguments,self.files,self.backrefs,self.username,self.backfiles,self.batchfiles,self.batch_switches,self.consume_switches])

    def deserialise(self, data):
        try:
            self.command, self.arguments,self.files,self.backrefs,self.username,self.backfiles,self.batchfiles,self.batch_switches,self.consume_switches = pickle.loads(str(data))
        except ImportError, ie:
            # might be caused by frontend editing causing \n's to be replaced with \r\n's
            self.command, self.arguments,self.files,self.backrefs,self.username,self.backfiles,self.batchfiles,self.batch_switches,self.consume_switches = pickle.loads(str(data).replace('\r\n','\n'))

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
        
    def _convert_filename(self, filename):
        return self.uri_conversion_string%{'filename':filename}

    def render(self, batchfiles={}):
        """renders the command template into a string. needs to be passed a dictionary of the batch files"""
        print "render:",batchfiles
        self.batchfiles = batchfiles
        
        output = self.command.render()
        
        for argument in self.arguments:
            if argument.takes_input_file:
                assert len(batchfiles), "batch_files passed in has %d entries which is not enough for command tempate %r"%(len(self.batchfiles),self)
                #print "batchfiles: %s"%(batchfiles)
                #print "argument: %s"%(argument)
                #print "flag: %s"%(argument.flag)
                # render all in a list
                try:
                    output += " "+argument.render([self._convert(X) for X in batchfiles[argument.flag]])
                except KeyError:
                    logger.critical("Unable to find files for parameter %s" % argument.flag)
                    raise

            elif argument.takes_output_file:
                # find the base filename this switch requires
                #print "argument.source_switch=%s"%(argument.source_switch)
                base_name = batchfiles[argument.source_switch][0].rsplit("/")[-1]
                #print "basename=%s"%(base_name)
                #print "render=%s"%(argument.render(base_name))
                output += " "+argument.render(base_name)                                # pass it into the argument render function
            elif argument.needs_filename_conversion:
                # if this argument needs a conversion, we pass in a converter function for it to use
                output += " "+argument.render(lambda x: self._convert_filename(x))
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
                    if 'type' in value and (value['type']=='file' or value['type']=='directory'):                       # TODO: what if value is unicode and contains the word 'type' within it! LOL
                        # param refers to a file
                        assert tp.file_assignment=="batch" or tp.file_assignment=="all", "File parameter passed in on switch '%s' where file_assignment is neither 'batch' nor 'all'"%(tp.switch)
                        value['extensions'] = tp.input_filetype_patterns()
                        
                        # annotate with the switch we are processing
                        value['switch'] = tp.switch
                    
                        self.files.append(value)
                    else:
                        # switch has single parameter
                        if DEBUG:
                            if tp.batch_bundle_files:
                                print "!!!![%s] tool.batch_bundle_files"%(tp.switch)
                            if tp.input_file:
                                print "!!!![%s] tp.input_file"%(tp.switch)
                            if tp.output_file:
                                print "!!!![%s] tp.output_file"%(tp.switch)
                            if tp.use_output_filename:
                                print "!!!![%s] tp.use_output_filename = %s"%(tp.switch,tp.use_output_filename)
                            if tp.extension_param:
                                print "!!!![%s] tp.extension_param"%(tp.switch)
                        if type(value) is dict:
                            assert "type" in value and (value['type']=='job' or value['type']=='jobfile'), "Unknown param value type for switch '%s', type is '%s'"%(tp.switch,value['type'])           
                            
                            # annotate extra info
                            value['extensions'] = tp.input_filetype_patterns() 
                            value['bundle_files'] = tp.batch_bundle_files
                            value['file_assignment'] = tp.file_assignment
                            
                            # annotate with the switch we are processing
                            value['switch'] = tp.switch
                            
                            # save the param
                            self.backrefs.append(value)
                            if tp.file_assignment=="batch":                 #tp.batch_param:
                                # this is a batch parameter, so it needs the special batch switch
                                self.arguments.append( BatchSwitch( tp.switch, switchuse=tp.switch_use.formatstring ) )
                                self.batch_switches.append(tp.switch)
                                
                            elif tp.file_assignment=="all":
                                # this is a consume parameter. so it needs the consumer switch
                                self.arguments.append( ConsumerSwitch( tp.switch, switchuse=tp.switch_use.formatstring ) )
                                self.consume_switches.append(tp.switch)
                                                                
                            else:
                                if 'filename' in value:
                                    # this is just an input file that will be staged along. lets add the filename statically now as it wont change, then we use the uri conversion later to make it full path
                                    self.arguments.append( Switch( tp.switch, SwitchInputFilename(value['filename']), switchuse=tp.switch_use.formatstring ) )
                                else:
                                    assert value['type']=='job' and 'jobId' in value, "non previous job switch input filename. value is: %s"%(str(value))
                                    self.arguments.append( UnknownFileSwitch( tp.switch, value, switchuse=tp.switch_use.formatstring ) )
                            
                        elif type(value) is str or type(value) is unicode:
                            value = quote_argument( value )
                            
                            if tp.output_file:
                                if tp.use_output_filename:
                                    # this means output filename has to be named after the filename associated with the switch this parameter is pointing to
                                    if tp.extension_param:
                                        value = SwitchFilename(default=value, template=make_fname, source_switch=tp.use_output_filename.switch, extension=tp.extension_param.extension() )
                                    else:
                                        value = SwitchFilename(default=value, source_switch=tp.use_output_filename.switch)
                                
                            self.arguments.append( Switch( tp.switch, value, switchuse=tp.switch_use.formatstring ) )
    
    def get_dependencies(self):
        # at this point, some of the backrefs may have resolved themselves
        # we should update the backrefs to reflect the new state
        return len(self.backrefs)
    dependencies = property(get_dependencies)
    
    def update_dependencies(self, workflow, ignore_glob_list=[]):
        """ignore_glob_list is a list of filename globbing patterns of files to exclude from use in any jobs"""
        new_backrefs=[]
        for backref in self.backrefs:
            assert 'type' in backref and (backref['type']=="job" or backref['type']=='jobfile')                     # TODO: support jobfile correctly
            job_index = backref['jobId']-1
            
            # get this job its referring to
            job = workflow.get_job(job_index)
            stageout = job.stageout
            
            # has the job finished?
            if job.status == "complete":    
                # do we now have files for this old job?
                file_list = backendhelper.get_file_list(self.username, stageout)
                if len(file_list):
                    # if it's a 'jobfile' then we need to select just the specified file.
                    if backref['type']=='jobfile':
                        # SINGLE FILE
                        # file must appear in list
                        assert backref['filename'] in [X[0] for X in file_list], "Selected input file does not appear in output of previous tool"
                        index = [X[0] for X in file_list].index(backref['filename'])
                        filename, size, date, link = file_list[index]
                        details = {
                            "path" : [],
                            "filename" : filename,
                            "type" : "file",
                            "root" : stageout,
                            "pathComponents" : [ stageout ],
                            "extensions" : backref['extensions'],
                            "switch" : backref['switch']
                        }
                        if backref['file_assignment']=='batch' or backref['file_assignment']=='all':
                            # its a single batch file. add it to backfiles
                            if backref['switch'] not in self.backfiles:
                                #print "self: %s backfiles: %s"%(str(self), str(self.backfiles))
                                self.backfiles[backref['switch']]=[]
                            self.backfiles[backref['switch']].append(details)
                        else:
                            # its a single file passed in via a param
                            self.files.append(details)                           
                    else:
                        assert backref['type']=='job'
                        # BUNCH OF FILES
                        # this refers to a entire job, not a specific file.
                        # if the parameter is batch_param, we batch all the files
                        # if its not batch_param we only reference the FIRST matching file (this is legacy behavoir)
                        
                        ignore_future_matches = False               # this is for non batch_param args so we only get the first, but continue to process the rest (TODO: do we need to process the rest?)
                        
                        for filename, size, date, link in file_list:
                            if True in [fnmatch.fnmatch(filename.upper(), glob.upper()) for glob in ignore_glob_list]:
                                continue                        # skip this filename because it matches the glob ignore list
                                
                            details = {
                                    "path" : [],
                                    "filename" : filename,
                                    "type" : "file",
                                    "root" : stageout,
                                    "pathComponents" : [ stageout ],
                                    "extensions" : backref['extensions'],
                                    "switch" : backref['switch']
                                }
                            
                            
                            if backref['bundle_files']:
                                # this file should be forced into the file list
                                self.files.append(details)
                            
                            if backref['file_assignment']=='batch' or backref['file_assignment']=='all':
                                # this is a file BUNDLE, so it MUST be batch, or consume
                                for pattern in backref['extensions']:
                                    if fnmatch.fnmatch(filename.upper(), pattern.upper()):
                                        if backref['switch'] not in self.backfiles:
                                            self.backfiles[backref['switch']]=[]
                                        #print "Adding %s to batckfiles switch %s"%(filename,backref['switch'])
                                        self.backfiles[backref['switch']].append(details)
                                        break
                           
                            if 'extensions' in backref:
                                # if an UnknownFileSwitch argument refers back to THIS backref, then resolve the filename in the UnknownFileSwitch to this file if it matches
                                for arg in self.arguments:
                                    #print "> %s"%(str(arg))
                                    if arg.__class__ is UnknownFileSwitch:                          # TODO: Ducktyping fixing
                                        if arg.is_value(backref):
                                            # this is our backref arg
                                            if not arg.is_value_resolved():
                                                for pattern in backref['extensions']:
                                                    if fnmatch.fnmatch(filename.upper(), pattern.upper()):
                                                        #print "setting value of %s to %s"%(arg,filename)
                                                        arg.set_value(filename)
                                                        
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
                if DEBUG:
                    print "Other Files:",file
                    
                yield file
        
    def batch_files(self):
        """Like stageins but only those files assosicated with this rendering instance of the template as batch files
        Returns remote fs paths, not URIs
        """
        #print "Batchfiles=%s"%(self.batchfiles)
        for key,selection in self.batchfiles.items():
            if DEBUG:
                print "Batch File:",key,selection
            yield key,selection
            
    def all_files(self):
        """This, when called post render, returns all the files needed to stagein"""
        for file in self.other_files():
            #print "otherfile:%s"%(file)
            yield None,[file]
            
        for key,files in self.batch_files():
            #print "batchfile:%s"%(file)
            yield key,files
    
    def file_sets(self):
        """This returns all the filesets to pass to various renders of this command template.
        This is a sequence of parameters. Each item in the sequence is a dictionary.
        for tools taking batch params, each item in the quequence represents one batch job.
        for tools consuming all input files, there is only one item in the sequence, and it represents every file being consumed by a task, organised by input flag.
        """
        
        # first, get how the batch parameters look
        batch_set = [X for X in self.possible_batch_files()]
        
        # if there are no batch sets, just return the consume set
        if not batch_set:
            return self.possible_consume_files()
        
        # there are some batch. For each batch set in the sequence, add in all the consume set
        consume_set = [X for X in self.possible_consume_files()][0]
        
        for fileset in batch_set:
            #print "updating",fileset,"with",consume_set
            fileset.update(consume_set)
            
        #print "RETURNING:",batch_set
        return batch_set
        
    def possible_consume_files(self):
        """This returns a single itemed sequence consuming all possible files into the one fileset for passing to render.
        """
        if not len(self.backfiles):
            return
        
        out_hash = {}
        
        # for each switch that is in consume_switches
        for switch in [X for X in self.backfiles.keys() if X in self.consume_switches]:
            out_hash[switch] = []
            for details_hash in self.backfiles[switch]:
                out_hash[switch].extend( self.parse_param_value(details_hash) )
            out_hash[switch].sort(key=lambda path:os.path.basename(path))
        
        yield out_hash              # only one item in this sequence.        
            
    
    def possible_batch_files(self):
        """This returns all possible input batch files for this command template. Not just those used by this render.
        This generator is used to return all the possibilities for batch. From this we call render on each one to derive a task
        
        This returns the files as a dictionary of files with the key being the switch and the value being the uri
        """
        #print "APBF",self.backfiles
        
        if not len(self.backfiles):
            return
        
        # now we take each list of backfiles and group them together based on filename similarity.
       
        # only use keys that are batch switches
        set_keys = [X for X in self.backfiles.keys() if X in self.batch_switches]
        
        # the key we loop over will be the key with the most entries (or the first if they are all the same)
        lengths = [len(self.backfiles[X]) for X in set_keys]
        #print "set keys: %s lengths: %s"%(str(set_keys),str(lengths))
        if not lengths:
            return
            
        primary_key_index = lengths.index(max(lengths))
        primary_set_key = set_keys[primary_key_index]
        
        # all the other keys we need to process each loop
        other_set_keys = [X for X in set_keys if X != primary_set_key]
        
        #print "PRIMARY SET KEY: %s SECONDARY SET KEYS: %s"%(primary_set_key,str(other_set_keys))
        
        primary_set = self.backfiles[primary_set_key]       # the set of files to loop over
        
        output = []         # out output list
        
        for details_hash in primary_set:
            filename = details_hash['filename']             # the filename we have to find the most similar other filename to
            #batch_type = details_hash['batch_type']         # consume all or batch
            batch_set = {primary_set_key:details_hash}
            
            # for each other set
            for compare_key in other_set_keys:
                # for each other details
                distances = {}
                for num, compare_details in enumerate(self.backfiles[compare_key]):
                    compare_filename = compare_details['filename']
                    distance = levenshtein(filename, compare_filename)
                    
                    #print "the distance between %s and %s is %d"%(filename,compare_filename,distance)
       
                    # store the distance as a key and the self.backfiles[compare_key] subindex number as the value
                    assert distance not in distances, "two valid filenames have the same levenshtein distance"
                    distances[distance] = num
                
                # now we find the minimum distance
                min_distance = min(distances.keys())
                
                # now we get that detail entry
                matching_entry = self.backfiles[compare_key][distances[min_distance]]
                
                #print "Filename: %s matches up with %s"%(filename,matching_entry['filename'])
        
                batch_set[compare_key]=matching_entry
                
            #print "BATCH_SET: %s"%(str(batch_set))
            
            # now process the values of batch_set into parsed_param_values
            out_hash = {}
            for key,val in batch_set.iteritems():
                decoded_file_list = self.parse_param_value(val)
                assert len(decoded_file_list)==1
                out_hash[key] = decoded_file_list
            
            #print "YIELDING:",out_hash
            yield out_hash
        
        
        return
    
    def parse_param_value(self,item):
        if item['type'] == 'file':
            # decode file params
            return [self.parse_param_file_value(item)]
        
        elif item['type'] == 'directory':
            # if we are not select file
            if not self.command.is_select_file:
                # decode directory
                return [file for file in self.parse_param_directory_value(item)]
            else:
                # select file returns the directory itself, so rcopy can be used on the backend to preserve directory structures
                return [item['root']+item['filename']+"/"]
    
    def parse_param_file_value(self, item):
        path = ''
        if item['path']:
            path = os.path.join(*item['path'])
            if not path.endswith(os.sep):
                    path = path + os.sep
        return '%s%s%s' % (item['root'], path, item['filename'])
        
    def parse_param_directory_value(self, item):
        fulluri = "".join(item['pathComponents'])+'/'+item['filename']+'/'

        # get recursive directory listing
        filelist = backendhelper.get_file_list(self.username, fulluri, recurse=True)
        return [ fulluri + X[0] for X in filelist ] 
     
