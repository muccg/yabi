from django.conf import settings
import logging, logging.handlers
import os, socket

loggers = {}
DEBUG=logging.DEBUG
INFO=logging.INFO
WARNING=logging.WARNING
CRITICAL=logging.CRITICAL
FATAL=logging.FATAL

def getLogger(name):
    if name not in loggers:
        return logging.getLogger(name) #return python root based named logger
    else:
        return loggers[name]

def init_logger(name = "mango", logfile = "mango.log"):
    print "init logger %s " % logfile

    logger = logging.getLogger(name)
    logger.setLevel(settings.LOGGING_LEVEL)

    # add file system handler
    if not hasattr(logger, 'filehandler_added'):    
        handler = logging.handlers.TimedRotatingFileHandler(os.path.join(settings.LOG_DIRECTORY, logfile), 'midnight')
        handler.setFormatter(settings.LOGGING_FORMATTER)
        logger.addHandler(handler)
        logger.filehandler_added = True


    # add syslog handler
    if not hasattr(logger, 'sysloghandler_added'):
        try:
            handler = logging.handlers.SysLogHandler(address='/dev/log', facility='local4')
            handler.setFormatter(settings.LOGGING_FORMATTER)
            logger.addHandler(handler)
            logger.sysloghandler_added = True
        except socket.error, e:
            print "Unable to open syslog logger: %s" % e
            
    return logger


def init():
    """Initialise the logger from the settings file..."""
    
    for logname in settings.LOGS:
        loggers[logname] = init_logger(logname, "%s.log"%logname)

init()
