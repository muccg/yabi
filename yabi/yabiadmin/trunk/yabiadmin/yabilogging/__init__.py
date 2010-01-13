# -*- coding: utf-8 -*-
from django.conf import settings
import logging, logging.handlers

def init_logging():
    # yabiengine log
    fh = logging.handlers.TimedRotatingFileHandler(settings.LOG_DIRECTORY + '/yabiengine.log', 'midnight')
    fmt = logging.Formatter(settings.LOGGING_FORMATTER)
    print "FMT:",fmt
    fh.setFormatter(fmt)
    yabienginelogger = logging.getLogger('yabiengine')
    yabienginelogger.setLevel(settings.LOGGING_LEVEL)
    yabienginelogger.addHandler(fh)

    # yabiadmin log
    fh = logging.handlers.TimedRotatingFileHandler(settings.LOG_DIRECTORY + '/yabiadmin.log', 'midnight')
    fh.setFormatter(logging.Formatter(settings.LOGGING_FORMATTER))
    yabiadminlogger = logging.getLogger('yabiadmin')
    yabiadminlogger.setLevel(settings.LOGGING_LEVEL)
    yabiadminlogger.addHandler(fh)


logInitDone=False
if not logInitDone:
    logInitDone = True
    init_logging()
