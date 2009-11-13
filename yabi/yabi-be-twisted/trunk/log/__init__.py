import logging
import os

LOG_FILENAME = '/tmp/logging_example-%d.out'%os.getpid()

logging.basicConfig(filename=LOG_FILENAME,format='%(asctime)s %(levelname)s %(message)s',level=logging.DEBUG,)

# bind in the functions so we can just call log.debug, log.
debug = logging.debug
info = logging.info
warning = logging.warning
