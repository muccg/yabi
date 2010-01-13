# -*- coding: utf-8 -*-
from django.conf import settings
import logging, logging.handlers

def init_logging():
    # yabiengine log
    print "1"
    fh = logging.handlers.TimedRotatingFileHandler(settings.LOG_DIRECTORY + '/yabiengine.log', 'midnight')
    fh.setFormatter(logging.Formatter(settings.LOGGING_FORMATTER))
    yabienginelogger = logging.getLogger('yabiengine')
    yabienginelogger.setLevel(settings.LOGGING_LEVEL)
    yabienginelogger.addHandler(fh)

    print "2"
    # yabiadmin log
    fh = logging.handlers.TimedRotatingFileHandler(settings.LOG_DIRECTORY + '/yabiadmin.log', 'midnight')
    fh.setFormatter(logging.Formatter(settings.LOGGING_FORMATTER))
    yabiadminlogger = logging.getLogger('yabiadmin')
    yabiadminlogger.setLevel(settings.LOGGING_LEVEL)
    yabiadminlogger.addHandler(fh)

    print "done"

logInitDone=False
if not logInitDone:
    logInitDone = True
    init_logging()
