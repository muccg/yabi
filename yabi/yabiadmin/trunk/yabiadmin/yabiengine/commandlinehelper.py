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

from yabiadmin.yabmin.models import Backend, BackendCredential, Tool, User
from yabiadmin.yabiengine import backendhelper
from yabiadmin.yabiengine.models import Workflow, Task, Job
from yabiadmin.yabiengine.urihelper import uriparse, url_join


import logging
logger = logging.getLogger('yabiengine')


class CommandLineHelper():

    job = None
    job_dict = []
    command = []
    param_dict = {}
    job_cache = []

    _job_stageins = []
    _batch_files = []

    @property
    def batch_files(self):
        return repr(self._batch_files)

    @property
    def jobstageins(self):
        return repr(list(set(self._job_stageins))) # using set to remove duplicates
    
    def __init__(self, job):
        self.job = job
        self.job_dict = job.job_dict
        self.job_cache = job.workflow.job_cache

        self._job_stageins = []
        self._batch_files= []
        self.command = []

        logger.debug('')

        tool = Tool.objects.get(name=self.job_dict["toolName"])

        # process the parameterList to get a useful dict
        logger.debug("Process parameterList")
        self.param_dict = {}
        for toolparam in self.job_dict["parameterList"]["parameter"]:
            self.param_dict[toolparam["switchName"]] = self.get_param_value(toolparam)
        
        self.command.append(tool.path)

        for tp in tool.toolparameter_set.order_by('rank').all():

            # check the tool switch against the incoming params
            if tp.switch not in self.param_dict:
                logger.info("Switch ignored [%s]" % tp.switch)
                continue

            # if the switch is the batch on param switch put it in batch_files and add placeholder in command
            if tp == tool.batch_on_param:
                self._batch_files.extend(self.param_dict[tp.switch])
                self.param_dict[tp.switch] = ['%'] # use place holder now in self.command

            else:
                # add to job level stagins, later at task level we'll check these and add a stagein if needed
                self._job_stageins.extend(self.param_dict[tp.switch])

                
            # run through all the possible switch uses
            switchuse = tp.switch_use.value

            if switchuse == 'switchOnly':
                self.command.append(tp.switch)

            elif switchuse == 'valueOnly':
                self.command.append(self.param_dict[tp.switch][0])

            elif switchuse == 'both':
                self.command.append("%s %s" % (tp.switch, self.param_dict[tp.switch][0]))

            elif switchuse == 'combined':
                self.command.append("%s%s" % (tp.switch, self.param_dict[tp.switch][0]))

            elif switchuse == 'pair':
                raise Exception('Unimplemented switch type: pair')
        
            elif switchuse == 'none':
                pass

            else:
                logger.info("Unknown switch ignored [%s]" % tp.switch)
                raise Exception("Unknown switch type:  %s" % tp.switch)


    def get_param_value(self, param):
        '''
        This method takes the dict associated with a single parameter
        and returns a list of files for that parameter
        '''
        logger.debug("======= get_param_value =============: %s" % param)
        # TODO see if we can unwind this a little and comment thoroughly
        
        assert(type(param["value"]) == list)

        value = []

        for item in param["value"]:

            # if the items a dict it is referring to a file
            if type(item) == dict:

                # handle links to previous nodes
                if 'type' in item and 'jobId' in item:
                    previous_job = self.job_cache[item['jobId']]
                    filename = item.get('filename', '')
                    value = [u"%s%d/%d/%s" % (settings.YABI_URL, self.job.workflow.id, previous_job.id, filename)]


                # handle links to previous file selects
                elif 'type' in item and 'filename' in item and 'root' in item:

                    # files
                    if item['type'] == 'file':
                        path = ''
                        if item['path']:
                            path = os.path.join(*item['path'])
                            if not path.endswith(os.sep):
                                path = path + os.sep
                        value.append( '%s%s%s' % (item['root'], path, item['filename']) )

                    # directories
                    elif item['type'] == 'directory':
                        fulluri = item['root']+item['filename']+'/'

                        # get recursive directory listing
                        filelist = backendhelper.get_file_list(self.job.workflow.user.name, fulluri, recurse=True)
                        value.extend( [ fulluri + X[0] for X in filelist ] )


            # if item is not a dict then it is a plain parameter, not one referring to a file            
            elif type(item) == str or type(item) == unicode:
                value.append( item )
        
        return value
