# Remote S3-like storage backends for YABI.
# Copyright (C) 2014  Centre for Comparative Genomics

import logging
import threading

from .fsbackend import FSBackend
from .exceptions import NotSupportedError
import dateutil

logger = logging.getLogger(__name__)

NEVER_A_SYMLINK = False
DELIMITER = '/'

ERROR_STATUS = -1
OK_STATUS = 0


class KeyValueBackend(FSBackend):
    """
    A file backend implemented with buckets full of filename keys.
    """

    def fifo_to_remote(self, uri, fifo_name, queue=None):
        if queue is None:
            queue = NullQueue()
        logger.debug("upload_file %s -> %s", fifo_name, uri)
        thread = threading.Thread(target=self.upload_file, args=(uri, fifo_name, queue))
        thread.start()
        return thread

    def remote_to_fifo(self, uri, fifo_name, queue=None):
        if queue is None:
            queue = NullQueue()
        logger.debug("download_file %s <- %s", fifo_name, uri)
        thread = threading.Thread(target=self.download_file, args=(uri, fifo_name, queue))
        thread.start()
        return thread

    @classmethod
    def ensure_trailing_slash(cls, uri):
        return uri if uri.endswith(DELIMITER) else uri + DELIMITER

    # this overrides the one in FSBackend, need to check if it's ok
    def basename(self, key_name, delimiter=None):
        delimiter = DELIMITER if delimiter is None else delimiter
        name = key_name.rstrip(delimiter)
        delimiter_last_position = name.rfind(delimiter)
        return name[delimiter_last_position + 1:]

    @staticmethod
    def format_iso8601_date(iso8601_date):
        date = dateutil.parser.parse(iso8601_date)
        return date.strftime("%a, %d %b %Y %H:%M:%S")

    def local_copy(self, source, destination):
        raise NotSupportedError()

    def symbolic_link(self, source, destination):
        raise NotSupportedError()

    # Implementation

    def parent_dir_uri(self, uri):
        uri = uri.rstrip(DELIMITER)
        return uri[:uri.rfind(DELIMITER)] + DELIMITER


class NullQueue(object):
    def put(self, value):
        pass
