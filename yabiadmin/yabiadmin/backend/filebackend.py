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
from yabiadmin.backend.utils import ls
from yabiadmin.backend.exceptions import RetryException, FileNotFoundError
from yabiadmin.yabiengine.urihelper import uriparse
import os
import shutil
import logging
import traceback
import threading
logger = logging.getLogger(__name__)


LS_PATH = '/bin/ls'
LS_TIME_STYLE = r"+%b %d  %Y"

class FileBackend(FSBackend):
    def upload_file(self, uri, src, queue):
        scheme, parts = uriparse(uri)
        self._copy_file(open(src, "rb"), open(parts.path, "wb"), queue)

    def download_file(self, uri, dst, queue):
        scheme, parts = uriparse(uri)
        if not os.path.exists(parts.path):
            raise FileNotFoundError(uri)
        self._copy_file(open(parts.path, "rb"), open(dst, "wb"), queue)

    def _copy_file(self, src, dst, queue):
        success = False
        logger.debug('CopyThread {0} -> {1}'.format(src, dst))
        logger.debug('CopyThread start copy')
        try:
            shutil.copyfileobj(src, dst)
        except Exception as exc:
            # fixme: just catch the shutil and ioerror exceptions
            logger.exception("FileBackend _copy_file error")
        else:
            logger.debug('CopyThread end copy')
            success = True
        finally:
            queue.put(success)

    def remote_uri_stat(self, uri):
        scheme, parts = uriparse(uri)
        remote_path = parts.path
        stat = os.stat(remote_path)

        return { 'atime': stat.st_atime, 'mtime': stat.st_mtime }

    def set_remote_uri_times(self, uri, atime, mtime):
        scheme, parts = uriparse(uri)
        remote_path = parts.path

        os.utime(remote_path, (atime, mtime))

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
        except OSError as ose:
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
        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

    def local_copy_recursive(self, src_uri, dst_uri):
        """A local copy within this backend."""
        logger.debug('local_copy {0} -> {1}'.format(src_uri, dst_uri))
        src_scheme, src_parts = uriparse(src_uri)
        dst_scheme, dst_parts = uriparse(dst_uri)
        try:
            for item in os.listdir(src_parts.path):
                src = os.path.join(src_parts.path, item)
                dst = os.path.join(dst_parts.path, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

    def symbolic_link(self, target_uri, link_uri):
        """symbolic link to target_uri called link_uri."""
        logger.debug('symbolic_link {0} -> {1}'.format(link_uri, target_uri))
        target_scheme, target_parts = uriparse(target_uri)
        link_scheme, link_parts = uriparse(link_uri)
        try:
            os.symlink(target_parts.path, link_parts.path)
        except OSError as ose:
            raise RetryException(ose, traceback.format_exc())

    def rm(self, uri):
        """rm uri"""
        logger.debug('rm {0}'.format(uri))
        scheme, parts = uriparse(uri)
        logger.debug('{0}'.format(parts.path))

        if not os.path.exists(parts.path):
            raise Exception('rm target ({0}) is not a file or directory'.format(parts.path))

        try:
            path = parts.path.rstrip('/')
            if os.path.isfile(path) or os.path.islink(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

