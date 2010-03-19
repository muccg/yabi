# -*- coding: utf-8 -*-
from os.path import splitext
import os
import uuid
from math import log10
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from yabiadmin.yabiengine.models import Task, Job, Workflow, Syslog, StageIn
from yabiadmin.yabiengine.enginemodels import EngineJob
from yabiadmin.yabmin.models import Backend, BackendCredential
from yabiadmin.yabiengine.YabiJobException import YabiJobException
from yabiadmin.yabiengine.urihelper import uriparse, url_join
from yabiadmin.yabiengine import backendhelper

import logging
logger = logging.getLogger('yabiengine')

from conf import config







## TODO REFACTOR move this method onto enginejob
## TODO need a new method that will take a list of files and job param and return a list of those files that are valid
## this can then be used in wrangler to determine which file can be used for each non-batching param
## def is_task_file_valid(job,file):
##     """returns a boolean shwoing if the file passed in is a valid file for the job. Only uses the file extension to tell"""
##     return splitext(file)[1].strip('.') in job.extensions






