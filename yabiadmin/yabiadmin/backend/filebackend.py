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
from yabiadmin.backend.fsbackend import FSBackend
from yabiadmin.backend.utils import create_fifo, execute,ls
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.backend.parsers import parse_ls
from yabiadmin.yabiengine.urihelper import uriparse
import os
import shutil
import logging
import traceback
import threading
import subprocess
import Queue
logger = logging.getLogger(__name__)


LS_PATH = '/bin/ls'
LS_TIME_STYLE = r"+%b %d  %Y"


class CopyThread(threading.Thread):

    def __init__(self, src, dst, purge=None, queue=None):
        threading.Thread.__init__(self)
        self.src = src
        self.dst = dst
        self.purge = purge
        self.queue = queue

    def run(self):
        status = -1
        logger.debug('CopyThread {0} -> {1}'.format(self.src, self.dst))
        try:
            logger.debug('CopyThread start copy')
            shutil.copyfileobj(open(self.src, 'r'), open(self.dst, 'w'))
            #shutil.copyfileobj(open(self.src, os.O_RDONLY), open(self.dst, 'w+'))
            #shutil.copyfileobj(os.open(self.src, os.O_RDONLY), os.open(self.dst, os.O_WRONLY|os.O_CREAT))
            logger.debug('CopyThread end copy')
            status = 0
        except Exception, exc:
            logger.error(traceback.format_exc())
            logger.error(exc)
        finally:
            if self.queue is not None:
                self.queue.put(status)
            # I was using purge to optionally remove a fifi after a copy
            if self.purge is not None and os.path.exists(self.purge):
                os.unlink(self.purge)


class FileBackend(FSBackend):

    def fifo_to_remote(self, uri, fifo, queue=None):
        """initiate a copy from local fifo to uri"""
        scheme, parts = uriparse(uri)
        assert  os.path.exists(fifo)
        # purge the fifo after we finish reading from it
        thread = CopyThread(src=fifo, dst=parts.path, purge=fifo, queue=queue)
        thread.start()
        return thread

    def remote_to_fifo(self, uri, fifo, queue=None):
        """initiate a copy from local file to fifo"""
        scheme, parts = uriparse(uri)
        assert  os.path.exists(parts.path)
        assert  os.path.exists(fifo)
        thread = CopyThread(src=parts.path, dst=fifo, queue=queue)
        thread.start()
        return thread

    def isdir(self, uri):
        """is the uri a dir?"""
        scheme, parts = uriparse(uri)
        return os.path.exists(parts.path) and os.path.isdir(parts.path)

    def mkdir(self, uri):
        """mkdir at uri"""
        logger.debug('mkdir {0}'.format(uri))
        scheme, parts = uriparse(uri)

        if os.path.exists(parts.path) and os.path.isdir(parts.path):
            return

        try:
            os.makedirs(parts.path)
        except OSError, ose:
            raise RetryException(ose, traceback.format_exc())

    def ls_recursive(self, uri):
        """recursive ls listing at uri"""
        scheme, parts = uriparse(uri)
        logger.debug('{0}'.format(parts.path))
        return ls(parts.path, recurse=True)

    def ls(self, uri):
        """ls listing at uri"""
        scheme, parts = uriparse(uri)
        logger.debug('{0}'.format(parts.path))
        return ls(parts.path)

    def local_copy(self, src_uri, dst_uri):
        """A local copy within this backend."""
        logger.debug('local_copy {0} -> {1}'.format(src_uri, dst_uri))
        src_scheme, src_parts = uriparse(src_uri)
        dst_scheme, dst_parts = uriparse(dst_uri)
        try:
            shutil.copy2(src_parts.path, dst_parts.path)
        except Exception, exc:
            raise RetryException(exc, traceback.format_exc())

    def symbolic_link(self, target_uri, link_uri):
        """symbolic link to target_uri called link_uri."""
        logger.debug('symbolic_link {0} -> {1}'.format(link_uri, target_uri))
        target_scheme, target_parts = uriparse(target_uri)
        link_scheme, link_parts = uriparse(link_uri)
        try:
            os.symlink(target_parts.path, link_parts.path)
        except OSError, ose:
            raise RetryException(ose, traceback.format_exc())

    def rm(self, uri):
        """rm uri"""
        logger.debug('rm {0}'.format(uri))
        scheme, parts = uriparse(uri)
        logger.debug('{0}'.format(parts.path))

        if not os.path.exists(parts.path):
            raise Exception('rm target ({0}) is not a file or directory'.format(parts.path))

        try:
            if os.path.isdir(parts.path):
                shutil.rmtree(parts.path)
            elif os.path.isfile(parts.path):
                os.unlink(parts.path)
        except Exception, exc:
            raise RetryException(exc, traceback.format_exc())
