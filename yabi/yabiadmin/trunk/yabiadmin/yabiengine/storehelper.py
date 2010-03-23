# -*- coding: utf-8 -*-
import httplib, os
import uuid
from urllib import urlencode
from os.path import splitext

from django.conf import settings

from conf import config

import logging
logger = logging.getLogger('yabiengine')

class StoreHelper():

    @staticmethod
    def update(workflow):

        resource = os.path.join(settings.YABISTORE_BASE,"workflows", workflow.user.name, str(workflow.id))
        data = {'json':workflow.json,
                'name':workflow.name,
                'status':workflow.status
                }

        data = urlencode(data)
        headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
        conn = httplib.HTTPConnection(settings.YABISTORE_SERVER)
        conn.request('POST', resource, data, headers)
        logger.debug("YABISTORE POST:")
        logger.debug(settings.YABISTORE_SERVER)
        logger.debug(resource)
        logger.debug(data)

        r = conn.getresponse()
    
        status = r.status
        data = r.read()
        assert status == 200    
        logger.debug("result:")
        logger.debug(status)
        logger.debug(data)
    
        return status,data





