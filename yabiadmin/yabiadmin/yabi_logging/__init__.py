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

import logging, logging.handlers
import os, socket


##
## LOGGING
##

# This setup is used by CCG to log to files and to syslog. You can alter it for your own setup.

PROJECT_DIRECTORY = os.environ['PROJECT_DIRECTORY']
LOG_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"logs")
LOGGING_LEVEL = logging.DEBUG
install_name = PROJECT_DIRECTORY.split('/')[-2]
LOGGING_FORMATTER = logging.Formatter('YABI [%(name)s:' + install_name + ':%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s')
LOGS = ['yabiengine','yabiadmin']

loggers = {}

def getLogger(name):
    if name not in loggers:
        return logging.getLogger(name) #return python root based named logger
    else:
        return loggers[name]

def init_logger(name = "mango", logfile = "mango.log"):
    #print "init logger %s " % logfile

    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_LEVEL)

    # add file system handler
    if not hasattr(logger, 'filehandler_added'):    
        handler = logging.handlers.TimedRotatingFileHandler(os.path.join(LOG_DIRECTORY, logfile), 'midnight')
        handler.setFormatter(LOGGING_FORMATTER)
        logger.addHandler(handler)
        logger.filehandler_added = True


    # add syslog handler
    if not hasattr(logger, 'sysloghandler_added'):
        try:
            handler = logging.handlers.SysLogHandler(address='/dev/log', facility='local4')
            handler.setFormatter(LOGGING_FORMATTER)
            logger.addHandler(handler)
            logger.sysloghandler_added = True
        except socket.error, e:
            print "Unable to open syslog logger: %s" % e
            
    return logger


def init():   
    for logname in LOGS:
        loggers[logname] = init_logger(logname, "%s.log"%logname)

init()
