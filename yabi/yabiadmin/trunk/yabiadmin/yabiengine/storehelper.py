# -*- coding: utf-8 -*-
import httplib, os
import uuid
from urllib import urlencode
from os.path import splitext

from django.conf import settings
from django.utils import simplejson as json

from yabiadmin.yabistoreapp import db

import logging
logger = logging.getLogger('yabiengine')


def archiveWorkflow(workflow):
    '''Save the workflow to Store an delete from here.
    '''
    logger.debug('')
    try:
        db.ensure_user_db(workflow.user.name)
        db.save_workflow(workflow.user.name, workflow, 
            [t.tag.value for t in workflow.workflowtag_set.all()])
    except Exception, e:
        logger.critical("Couldn't save workflow %d to store: %s" % 
                (workflow.id, e))
        raise 
        return False

    workflow.delete_cascade()
    return True
