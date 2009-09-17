from django.conf import settings
import logging, logging.handlers

def init_logging():

    # yabife log
    fh = logging.handlers.TimedRotatingFileHandler(settings.LOG_DIRECTORY + '/yabife.log', 'midnight')
    fh.setFormatter(settings.LOGGING_FORMATTER)
    yabifelogger = logging.getLogger('yabife')
    yabifelogger.setLevel(settings.LOGGING_LEVEL)
    yabifelogger.addHandler(fh)


logInitDone=False
if not logInitDone:
    logInitDone = True
    init_logging()
