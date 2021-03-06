# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from yabi.backend.fsbackend import FSBackend
from yabi.backend.utils import ls
from yabi.backend.exceptions import RetryException, FileNotFoundError
from yabi.yabiengine.urihelper import uriparse
import os
import shutil
import logging
import tarfile
import traceback


logger = logging.getLogger(__name__)


LS_PATH = '/bin/ls'
LS_TIME_STYLE = r"+%b %d  %Y"


class FileBackend(FSBackend):
    backend_desc = "File system"
    backend_auth = {}

    def upload_file(self, uri, src):
        scheme, parts = uriparse(uri)
        return self._copy_file(src, open(parts.path, "wb"))

    def download_file(self, uri, dst):
        scheme, parts = uriparse(uri)
        if not os.path.exists(parts.path):
            raise FileNotFoundError(uri)
        return self._copy_file(open(parts.path, "rb"), dst)

    def download_dir(self, uri, dst):
        scheme, parts = uriparse(uri)
        if not os.path.exists(parts.path):
            raise FileNotFoundError(uri)
        return self._tar_and_copy_dir(parts.path, dst)

    def _copy_file(self, src, dst):
        success = False
        logger.debug('CopyThread {0} -> {1}'.format(src, dst))
        logger.debug('CopyThread start copy')
        try:
            shutil.copyfileobj(src, dst)
        except Exception:
            # fixme: just catch the shutil and ioerror exceptions
            logger.exception("FileBackend _copy_file error")
        else:
            logger.debug('CopyThread end copy')
            success = True
        return success

    def _tar_and_copy_dir(self, src, dst):
        success = False
        logger.debug('TarAndCopyThread {0} -> {1}'.format(src, dst))
        logger.debug('TarAndCopyThread start tar')
        try:
            with tarfile.open(fileobj=dst, mode='w|gz') as f:
                f.add(src, arcname=os.path.basename(src.rstrip('/')))
        except Exception:
            logger.exception("FileBackend _tar_and_copy_dir error")
        else:
            logger.debug('TarAndCopyThread end tar')
            success = True
        return success

    def remote_uri_stat(self, uri):
        scheme, parts = uriparse(uri)
        remote_path = parts.path
        stat = os.stat(remote_path)

        return {'atime': stat.st_atime, 'mtime': stat.st_mtime}

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
        logger.debug('symbolic_link {0} -> {1}'.format(target_uri, link_uri))
        target_scheme, target_parts = uriparse(target_uri)
        link_scheme, link_parts = uriparse(link_uri)
        target = target_parts.path
        try:
            if not os.path.exists(target):
                raise FileNotFoundError("Source of symbolic link '%s' doesn't exist" % target)
            os.symlink(target, link_parts.path)
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
