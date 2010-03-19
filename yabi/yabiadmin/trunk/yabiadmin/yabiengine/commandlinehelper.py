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
    _job_stageins = []
    param_dict = {}
    job_cache = []

    # TODO should this be batch_list
    _commandparams = []

    @property
    def commandparams(self):
        return repr(self._commandparams)

    @property
    def jobstageins(self):
        return repr(list(set(self._job_stageins))) # using set to remove duplicates
    

    # TODO this si a little evil, we have a direct reference into workflow.job_cache
    # Move job cache out of the workflow or give a ref to workflow instead
    # Might be cleaner to give reference to the workflow, then we dont need to pass around
    # json, ORM, job caches and so on

    def __init__(self, job, job_dict=None, job_cache=None):
        self.job = job
        self.job_dict = job_dict
        self.job_cache = job_cache

        self._job_stageins = []
        self._commandparams= []
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
            # TODO Should this be the other way around, that is, make sure that the param in the
            # dict is in the db? (To prevent injection)
            if tp.switch not in self.param_dict:
                logger.info("Switch ignored [%]" % tp.switch)
                continue

            # if the switch is the batch on param switch put it in commandparams and add placeholder in command
            if tp == tool.batch_on_param:
                self._commandparams.extend(self.param_dict[tp.switch])
                self.param_dict[tp.switch] = ['%'] # use place holder now in self.command

            else:
                # add to job level stagins, later at task level we'll check these and add a stagein if needed
                self._job_stageins.extend(self.param_dict[tp.switch])

            logger.debug('++++++++++++++++++++++++++++++++++++++++')
            logger.debug(self.param_dict)
            logger.debug(tp.switch)
                
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

            # TODO else throw


    def get_param_value(self, tp):
        logger.debug('')

        logger.debug("======= get_param_value =============: %s" % tp)
        # TODO see if we can unwind this a little and comment thoroughly
        
        value = []
        if type(tp["value"]) == list:
            # parameter input is multiple input files. loop ofer these files
            for item in tp["value"]:

                if type(item) == dict:

                    # handle links to previous nodes
                    if 'type' in item and 'jobId' in item:
                        previous_job = self.job_cache[item['jobId']]

                        if previous_job.stageout == None:
                            value = eval(previous_job.commandparams)
                        else:
                            value = [u"%s%d/%d/" % (settings.YABI_URL, self.job.workflow.id, self.job_cache[item['jobId']].id)]
                        
                    # handle links to previous file selects
                    elif 'type' in item and 'filename' in item and 'root' in item:
                        if item['type'] == 'file':
                            path = ''
                            if item['path']:
                                path = os.path.join(*item['path'])
                                if not path.endswith(os.sep):
                                    path = path + os.sep
                            value.append( '%s%s%s' % (item['root'], path, item['filename']) )
                        elif item['type'] == 'directory':
                            fulluri = item['root']+item['filename']+'/'
                            
                            # get recursive directory listing
                            filelist = backendhelper.get_file_list(self.job.workflow.user.name, fulluri, recurse=True)
                            
                            logger.debug("FILELIST returned:%s"%str(filelist))
                        
                            value.extend( [ fulluri + X[0] for X in filelist ] )
                
                elif type(item) == str or type(item) == unicode:
                    value.append( item )

        return value
