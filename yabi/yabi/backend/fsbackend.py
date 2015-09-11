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
from __future__ import unicode_literals
import json
import os
from yabi.backend.exceptions import RetryException, NotSupportedError
from yabi.backend.utils import create_fifo, SaveExceptionThread
from yabi.backend.backend import fs_credential
from yabi.backend.basebackend import BaseBackend
from yabi.backend.pooling import get_ssh_pool_manager
from yabi.yabiengine.urihelper import url_join, uriparse, is_same_location
from yabi.yabiengine.engine_logging import create_task_logger
from yabi.constants import ENVVAR_FILENAME
import dateutil.parser
import logging
import traceback
import Queue
from six.moves import map


logger = logging.getLogger(__name__)

pool_manager = get_ssh_pool_manager()


def stream_watcher(identifier, stream):

    # TODO
    # Can we pass through a ref to the process?
    # Can we unlink the fifo after read/write is done?
    # change to process_watcher and have one thread per process?
    for line in stream:
        logger.warning('{0} {1}'.format(identifier, line))

    if not stream.closed:
        stream.close()


class FSBackend(BaseBackend):
    lcopy_supported = True
    link_supported = True

    @staticmethod
    def factory(task):
        assert(task)
        assert(task.fsscheme)

        backend = FSBackend.create_backend_for_scheme(task.fsscheme)
        if backend is None:
            raise Exception('No valid scheme ({0}) is defined for task {1}'.format(task.fsscheme, task.id))

        backend.task = task
        backend.yabiusername = task.job.workflow.user.name
        return backend

    @staticmethod
    def urifactory(yabiusername, uri):
        assert(uri)
        fsscheme, fsbackend_parts = uriparse(uri)

        backend = FSBackend.create_backend_for_scheme(fsscheme)
        if backend is None:
            raise Exception("No backend can be found for uri %s with fsscheme %s for user %s" % (uri, fsscheme, yabiusername))

        backend.yabiusername = yabiusername
        backend.cred = fs_credential(yabiusername, uri)
        return backend

    @staticmethod
    def remote_copy(yabiusername, src_uri, dst_uri):
        try:
            FSBackend.remote_copy_recurse(yabiusername, src_uri, dst_uri)
        finally:
            pool_manager.release()

    @staticmethod
    def remote_copy_recurse(yabiusername, src_uri, dst_uri):
        """Recursively copy src_uri to dst_uri"""
        logger.info('remote_copy {0} -> {1}'.format(src_uri, dst_uri))
        src_backend = FSBackend.urifactory(yabiusername, src_uri)
        dst_backend = FSBackend.urifactory(yabiusername, dst_uri)

        try:
            src_stat = src_backend.remote_uri_stat(src_uri)

            listing = src_backend.ls(src_uri)  # get _flat_ listing here not recursive as before
            dst_backend.mkdir(dst_uri)
            logger.debug("listing of src_uri %s = %s" % (src_uri, listing))
            for key in listing:
                # copy files using a fifo
                for listing_file in listing[key]['files']:
                    src_file_uri = url_join(src_uri, listing_file[0])
                    dst_file_uri = url_join(dst_uri, listing_file[0])
                    logger.debug("src_file_uri = %s" % src_file_uri)
                    logger.debug("dst_file_uri = %s" % dst_file_uri)
                    FSBackend.remote_file_copy(yabiusername, src_file_uri, dst_file_uri)

                # recurse on directories

                for listing_dir in listing[key]['directories']:
                    src_dir_uri = url_join(src_uri, listing_dir[0])
                    dst_dir_uri = url_join(dst_uri, listing_dir[0])
                    logger.debug("src_dir_uri = %s" % src_dir_uri)
                    logger.debug("dst_dir_uri = %s" % dst_dir_uri)
                    FSBackend.remote_copy_recurse(yabiusername, src_dir_uri, dst_dir_uri)

            if src_stat and src_backend.basename(src_uri.rstrip('/')) == dst_backend.basename(dst_uri.rstrip('/')):
                # Avoid setting the times if we're copying the contents of the source
                atime = src_stat.get('atime')
                mtime = src_stat.get('mtime')
                dst_backend.set_remote_uri_times(dst_uri, atime, mtime)
        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

    @staticmethod
    def remote_file_copy(yabiusername, src_uri, dst_uri):
        """Use a local fifo to copy a single file from src_uri to dst_uri"""
        logger.debug('remote_file_copy {0} -> {1}'.format(src_uri, dst_uri))

        # we need refs to the src and dst backends
        src_backend = FSBackend.urifactory(yabiusername, src_uri)
        dst_backend = FSBackend.urifactory(yabiusername, dst_uri)
        src_scheme, src_parts = uriparse(src_uri)
        dst_scheme, dst_parts = uriparse(dst_uri)
        # Making sure dst_uri is always a file not a dir
        if dst_parts.path.endswith("/"):  # Looks like a dir
            dst_file_uri = "%s/%s" % (dst_uri.rstrip('/'), src_backend.basename(src_parts.path))
            dst_scheme, dst_parts = uriparse(dst_uri)
        else:
            dst_file_uri = dst_uri

        fifo = None
        try:
            src_stat = src_backend.remote_uri_stat(src_uri)

            # create a fifo, start the write to/read from fifo
            fifo = create_fifo('remote_file_copy_' + yabiusername + '_' + src_parts.hostname + '_' + dst_parts.hostname)
            src_cmd, src_queue = src_backend.remote_to_fifo(src_uri, fifo)
            dst_cmd, dst_queue = dst_backend.fifo_to_remote(dst_file_uri, fifo)
            src_cmd.join()
            dst_cmd.join()
            try:
                os.unlink(fifo)
            except OSError:
                pass
            src_success = src_queue.get()
            dst_success = dst_queue.get()

            # check exit status
            if not src_success:
                raise RetryException('remote_file_copy remote_to_fifo failed')
            if not dst_success:
                raise RetryException('remote_file_copy fifo_to_remote failed')

            if src_stat:
                atime = src_stat.get('atime')
                mtime = src_stat.get('mtime')
                dst_backend.set_remote_uri_times(dst_file_uri, atime, mtime)

        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

    def _fifo_thread(self, method, uri, fifo_name, open_mode):
        queue = Queue.Queue()

        def run():
            success = False
            try:
                with open(fifo_name, open_mode) as fifo:
                    success = method(uri, fifo)
            except Exception:
                logger.exception("fifo thread operation %s failed." % method.__name__)
                raise
            finally:
                queue.put(success)

        thread = SaveExceptionThread(target=run)
        thread.start()
        return thread, queue

    def fifo_to_remote(self, uri, fifo_name):
        logger.debug("upload_file %s -> %s", fifo_name, uri)
        return self._fifo_thread(self.upload_file, uri, fifo_name, "rb")

    def remote_dir_to_fifo(self, uri, fifo_name):
        logger.debug("download dir %s <- %s", fifo_name, uri)
        return self._fifo_thread(self.download_dir, uri, fifo_name, "wb")

    def remote_to_fifo(self, uri, fifo_name):
        logger.debug("download_file %s <- %s", fifo_name, uri)
        return self._fifo_thread(self.download_file, uri, fifo_name, "wb")

    def upload_file(self, uri, fifo):
        raise NotImplementedError()

    def download_file(self, uri, fifo):
        raise NotImplementedError()

    def download_dir(self, uri, fifo):
        raise NotImplementedError()

    @staticmethod
    def remote_file_download(yabiusername, uri, is_dir=False):
        """Use a local fifo to download a remote file"""
        logger.debug('{0} -> local fifo'.format(uri))

        # we need ref to the backend
        backend = FSBackend.urifactory(yabiusername, uri)
        scheme, parts = uriparse(uri)

        try:
            # create a fifo, start the write to/read from fifo
            fifo = create_fifo('remote_file_download_' + yabiusername + '_' + parts.hostname)
            if is_dir:
                thread, queue = backend.remote_dir_to_fifo(uri, fifo)
            else:
                thread, queue = backend.remote_to_fifo(uri, fifo)

            infile = open(fifo, "rb")
            try:
                os.unlink(fifo)
            except OSError:
                logger.exception("Couldn't delete remote file download fifo")

            return infile, thread, queue

        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

    @staticmethod
    def remote_file_upload(yabiusername, filename, uri):
        """Use a local fifo to upload to a remote file"""
        logger.debug('local_fifo -> {0}'.format(uri))

        # we need ref to the backend
        backend = FSBackend.urifactory(yabiusername, uri)
        scheme, parts = uriparse(uri)

        # uri for an upload must specify filename. we can't rely on the
        # source name as we copy from a fifo with a random name
        if not uri.endswith(filename):
            if not uri.endswith('/'):
                uri = uri + '/'
            uri = uri + filename

        try:
            # create a fifo, start the write to/read from fifo
            fifo = create_fifo('remote_file_upload_' + yabiusername + '_' + parts.hostname)
            thread, queue = backend.fifo_to_remote(uri, fifo)

            outfile = open(fifo, "wb")
            try:
                os.unlink(fifo)
            except OSError:
                logger.exception("Couldn't delete remote file upload fifo")
            return outfile, queue
        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

    def save_envvars(self, task, envvars_uri):
        try:
            fifo, thread, queue = FSBackend.remote_file_download(self.yabiusername, envvars_uri)
            envvars = json.load(fifo)
        except:
            logger.exception("Could not read contents of envvars file '%s' for task %s", envvars_uri, task.pk)
        else:
            task.envvars_json = json.dumps(envvars)
            task.save()

    def _create_working_dir_structure(self):
        self.mkdir(self.working_dir_uri())
        self.mkdir(self.working_input_dir_uri())
        self.mkdir(self.working_output_dir_uri())

    def before_stage_in_files(self):
        self._create_working_dir_structure()

    def stage_in_files(self):
        self.before_stage_in_files()
        task_logger = create_task_logger(logger, self.task.pk)
        stageins = self.task.get_stageins()
        task_logger.info("About to stagein %d stageins", len(stageins))
        for stagein in stageins:
            backend = FSBackend.urifactory(self.yabiusername, stagein.src)
            backend.stage_in(stagein)
            if stagein.matches_filename(ENVVAR_FILENAME):
                self.save_envvars(self.task, stagein.src)

    def stage_in(self, stagein):
        """Perform a single stage in."""
        task_logger = create_task_logger(logger, stagein.task.pk)
        task_logger.info("Stagein: %sing '%s' to '%s'", stagein.method, stagein.src, stagein.dst)

        method = stagein.method
        if method == 'link' and not self.link_supported:
            method = 'lcopy'
        if method == 'lcopy' and not self.lcopy_supported:
            method = 'copy'
        if stagein.method != method:
            task_logger.info("Preferred stagein method '%s' not supported, changing it to '%s'", stagein.method, method)
            stagein.method = method
            stagein.save()

        if stagein.method == 'copy':
            if stagein.src.endswith('/'):
                FSBackend.remote_copy(self.yabiusername, stagein.src, stagein.dst)
            else:
                FSBackend.remote_file_copy(self.yabiusername, stagein.src, stagein.dst)

        if stagein.method == 'lcopy':
            if stagein.src.endswith('/'):
                self.local_copy_recursive(stagein.src, stagein.dst)
            else:
                self.local_copy(stagein.src, stagein.dst)

        if stagein.method == 'link':
            if stagein.src.endswith('/'):
                listing = self.ls(stagein.src).values()[0]
                for entry in listing['files'] + listing['directories']:
                    name, _, _, _ = entry
                    self.symbolic_link(url_join(stagein.src, name), url_join(stagein.dst, name))
            else:
                self.symbolic_link(stagein.src, stagein.dst)

    def stage_out_files(self):
        """
        Stage out files from fs backend to stageout area.
        """
        task_logger = create_task_logger(logger, self.task.pk)
        # first we need a stage out directory
        task_logger.info("Stageout to %s", self.task.stageout)
        backend_for_stageout = FSBackend.urifactory(self.yabiusername, self.task.stageout)
        backend_for_stageout.mkdir(self.task.stageout)

        # now the stageout proper
        method = self.task.job.preferred_stageout_method
        src = self.working_output_dir_uri()
        dst = self.task.stageout

        if method == 'lcopy' and not is_same_location(src, dst):
            method = 'copy'

        task_logger.info("Stageout: %sing '%s' to '%s'", method, src, dst)
        if method == 'lcopy':
            return self.local_copy_recursive(src, dst)

        if method == 'copy':
            return FSBackend.remote_copy(self.yabiusername, src, dst)

        raise RuntimeError("Invalid stageout method %s for task %s" % (method, self.task.pk))

    # TODO review later: maybe this should be static method or similar
    # feels strange we create the FSBackend with a factory based on task but then
    # we need to create another backend for the working_dir
    def clean_up_task(self):
        # remove working directory
        working_dir_backend = FSBackend.urifactory(self.yabiusername, self.working_dir_uri())
        # Don't fail just because we can't delete the working dir
        # We do log the error and proceed.
        try:
            working_dir_backend.rm(self.working_dir_uri())
        except:
            task_logger = create_task_logger(logger, self.task.pk)
            task_logger.exception("Couldn't delete working dir '%s' of task %s.", self.working_dir_uri(), self.task.pk)

    def ls_recursive(self, uri):
        result = self.ls(uri)

        dirs = []
        if result.values():
            dirs = result.values()[0].get('directories')

        dir_uris = map(lambda d: "%s/%s" % (uri.rstrip("/"), d[0].lstrip("/")), dirs)
        for d in dir_uris:
            result.update(self.ls_recursive(d))
        return result

    def set_cred(self, uri):
        from yabi.backend.backend import fs_credential
        self.cred = fs_credential(self.yabiusername, uri)

    def basename(self, path):
        return os.path.basename(path)

    def remote_uri_stat(self, uri):
        return {}

    def set_remote_uri_times(self, uri, atime, mtime):
        pass

    def rm(self, uri):
        raise NotImplementedError("")

    def mkdir(self, uri):
        raise NotImplementedError("")

    def ls(self, uri):
        raise NotImplementedError("")

    def local_copy(self, source, destination):
        raise NotSupportedError()

    def local_copy_recursive(self, source, destination):
        raise NotSupportedError()

    def symbolic_link(self, source, destination):
        raise NotSupportedError()

    @staticmethod
    def format_date(date):
        return format_date(date)

    @staticmethod
    def format_iso8601_date(iso8601_date):
        date = dateutil.parser.parse(iso8601_date)
        return format_date(date)


def format_date(date):
    return date.strftime("%a, %d %b %Y %H:%M:%S")
