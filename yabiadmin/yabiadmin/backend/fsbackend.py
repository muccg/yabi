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
import os
from yabiadmin.yabiengine.enginemodels import StageIn
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.backend.utils import create_fifo, execute
from yabiadmin.backend.backend import fs_credential
from yabiadmin.backend.basebackend import BaseBackend
from yabiadmin.yabiengine.urihelper import url_join, uriparse
import logging
import traceback
import shutil
import Queue
logger = logging.getLogger(__name__)


CP_PATH = '/bin/cp'


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


    @staticmethod
    def create_backend_for_scheme(fsscheme):
        backend = None

        if fsscheme == 'sftp' or fsscheme == 'scp':
            from yabiadmin.backend.sftpbackend import SFTPBackend
            backend = SFTPBackend()

        elif fsscheme == 'file' or fsscheme == 'localfs':
            from yabiadmin.backend.filebackend import FileBackend
            backend = FileBackend()

        elif fsscheme == 'select' or fsscheme == 'null':
            from yabiadmin.backend.selectfilebackend import SelectFileBackend
            backend = SelectFileBackend()

        elif fsscheme == 's3':
            from yabiadmin.backend.s3backend import S3Backend
            backend = S3Backend()

        return backend


    @staticmethod
    def factory(task):
        assert(task)
        assert(task.fsscheme)

        backend = FSBackend.create_backend_for_scheme(tasks.fsscheme)
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
        """Recursively copy src_uri to dst_uri"""
        logger.info('remote_copy {0} -> {1}'.format(src_uri, dst_uri))
        src_backend = FSBackend.urifactory(yabiusername, src_uri)
        dst_backend = FSBackend.urifactory(yabiusername, dst_uri)
        try:
            listing = src_backend.ls(src_uri)  # get _flat_ listing here not recursive as before
            dst_backend.mkdir(dst_uri)
            logger.debug("listing of src_uri %s = %s" % (src_uri, listing))
            for key in listing:
                # copy files using a fifo
                for listing_file in listing[key]['files']:
                    src_file_uri = url_join(src_uri,listing_file[0])
                    dst_file_uri = url_join(dst_uri, listing_file[0])
                    logger.debug("src_file_uri = %s" % src_file_uri)
                    logger.debug("dst_file_uri = %s" % dst_file_uri)
                    FSBackend.remote_file_copy(yabiusername, src_file_uri, dst_file_uri)

                # recurse on directories

                for listing_dir in listing[key]['directories']:
                    src_dir_uri = url_join(src_uri,listing_dir[0])
                    dst_dir_uri = url_join(dst_uri,listing_dir[0])
                    logger.debug("src_dir_uri = %s" % src_dir_uri)
                    logger.debug("dst_dir_uri = %s" % dst_dir_uri)
                    FSBackend.remote_copy(yabiusername, src_dir_uri, dst_dir_uri)
        except Exception, exc:
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
        if dst_parts.path.endswith("/"): # Looks like a dir
            dst_file_uri = "%s/%s" % (dst_uri, src_backend.basename(src_parts.path))
            dst_scheme, dst_parts = uriparse(dst_uri)
        else:
            dst_file_uri = dst_uri
        fifo = None
        try:
            # create a fifo, start the write to/read from fifo
            fifo = create_fifo('remote_file_copy_' + yabiusername + '_'+ src_parts.hostname + '_' + dst_parts.hostname)
            src_queue = Queue.Queue()
            dst_queue = Queue.Queue()
            src_cmd  = src_backend.remote_to_fifo(src_uri, fifo, src_queue)
            dst_cmd  = dst_backend.fifo_to_remote(dst_file_uri, fifo, dst_queue)
            src_cmd.join()
            dst_cmd.join()
            src_status = src_queue.get()
            dst_status = dst_queue.get()

            # check exit status
            if src_status != 0:
                raise RetryException('remote_file_copy remote_to_fifo failed')
            if dst_status != 0:
                raise RetryException('remote_file_copy fifo_to_remote failed')
        except Exception, exc:
            raise RetryException(exc, traceback.format_exc())

    @staticmethod
    def remote_file_download(yabiusername, uri):
        """Use a local fifo to download a remote file"""
        logger.debug('{0} -> local fifo'.format(uri))

        # we need ref to the backend
        backend = FSBackend.urifactory(yabiusername, uri)
        scheme, parts = uriparse(uri)
        try:
            # create a fifo, start the write to/read from fifo
            fifo = create_fifo('remote_file_download_' + yabiusername + '_' + parts.hostname)
            thread = backend.remote_to_fifo(uri, fifo)

            # TODO some check on the copy thread

            return fifo
        except Exception, exc:
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
            thread = backend.fifo_to_remote(uri, fifo)

            # TODO some check on the copy thread
            
            return fifo
        except Exception, exc:
            raise RetryException(exc, traceback.format_exc())

    def stage_in_files(self):
        self.mkdir(self.working_dir_uri())
        self.mkdir(self.working_input_dir_uri())
        self.mkdir(self.working_output_dir_uri())
        self.create_local_remnants_dir()

        stageins = self.task.get_stageins()
        for stagein in stageins:
            self.stage_in(stagein)

    def stage_in(self, stagein):
        """Perform a single stage in."""
        logger.debug(stagein.method)

        if stagein.method == 'copy':
            if stagein.src.endswith('/'):
                return FSBackend.remote_copy(self.yabiusername, stagein.src, stagein.dst)
            else:
                return FSBackend.remote_file_copy(self.yabiusername, stagein.src, stagein.dst)

        if stagein.method == 'lcopy':
            return self.local_copy(stagein.src, stagein.dst)

        if stagein.method == 'link':
            return self.symbolic_link(stagein.src, stagein.dst)

    def stage_out_files(self):
        """
        Stage out files from fs backend to stageout area.
        Also upload any local remnants of the task to the stageout area
        """
        # first we need a stage out directory
        backend_for_stageout = FSBackend.urifactory(self.yabiusername, self.task.stageout)
        backend_for_stageout.mkdir(self.task.stageout)

        # deal with any remanants from local commands
        self.stage_out_local_remnants()

        # now the stageout proper
        method = self.task.job.preferred_stageout_method
        logger.debug('stage out method is {0}'.format(method))
        if method == 'copy':
            return FSBackend.remote_copy(self.yabiusername, self.working_output_dir_uri(), self.task.stageout)

        if method == 'lcopy':
            return FSBackend.local_copy_recursive(self.yabiusername, self.working_output_dir_uri(), self.task.stageout)

    def stage_out_local_remnants(self):
        """
        stage out any local remanants
        some tasks/backends will leave remnants (STDERR/STDOUT) locally so we
        need to upload them to the stageout area
        """
        logger.debug('stage_out_local_remnants from {0}'.format(self.local_remnants_dir()))
        logger.debug('stage_out_local_remnants to {0}'.format(self.task.stageout))
        # stage out local remnants
        remnants_dir = self.local_remnants_dir()
        for (dirpath, dirnames, filenames) in os.walk(remnants_dir):
            for filename in filenames:
                # get a fifo to remote file
                uri = url_join(self.task.stageout, dirpath[len(remnants_dir):])
                logger.debug('uploading {0} to {1}'.format(filename, uri))
                upload_as_fifo = FSBackend.remote_file_upload(self.yabiusername, filename, uri)
                # write our remnant to the fifo
                remnant = os.path.join(dirpath, filename)
                #process = execute([CP_PATH, remnant, upload_as_fifo])
                #status = process.wait()

                try:
                    #shutil.copyfileobj(open(remnant, 'r'), open(upload_as_fifo, 'w+'))
                    shutil.copyfileobj(open(remnant, 'r'), open(upload_as_fifo, 'w'))
                except Exception, exc:
                    logger.error('copy to upload fifo failed')
                    raise RetryException(exc, traceback.format_exc())

                # check exit status
                #if status != 0:
                #    # TODO logger.error will fail with unicode errors
                #    logger.debug(str(process.stdout.read()))
                #    logger.debug(str(process.stderr.read()))
                #    raise RetryException('copy to upload fifo failed')

                #if os.path.exists(upload_as_fifo):
                #    os.unlink(upload_as_fifo)

            for dirname in dirnames:
                # any directories we encounter we create in the stageout area
                os.path.join(dirpath, dirname)
                uri = url_join(self.task.stageout, dirpath[len(remnants_dir):], dirname)
                self.mkdir(uri)

    @staticmethod
    def local_copy_recursive(yabiusername, src_uri, dst_uri):
        """Recursive local copy src_uri to dst_uri"""
        logger.debug('remote_copy {0} -> {1}'.format(src_uri, dst_uri))
        src_backend = FSBackend.urifactory(yabiusername, src_uri)
        dst_backend = FSBackend.urifactory(yabiusername, dst_uri)
        src_backend_class = src_backend.__class__.__name__
        logger.debug("src backend class = %s" % src_backend_class)
        dest_backend_class = dst_backend.__class__.__name__
        logger.debug("dst backend class = %s" % dest_backend_class)

        try:
            listing = src_backend.ls_recursive(src_uri)
            dst_backend.mkdir(dst_uri)
            for key in listing:
                # copy files using a fifo
                for listing_file in listing[key]['files']:
                    src_file_uri = url_join(src_uri, listing_file[0])
                    dst_file_uri = url_join(dst_uri, listing_file[0])
                    src_backend.local_copy(src_file_uri, dst_file_uri)
                # recurse on directories
                for listing_dir in listing[key]['directories']:
                    src_dir_uri = url_join(src_uri, listing_dir[0])
                    dst_dir_uri = url_join(dst_uri, listing_dir[0])
                    FSBackend.local_copy_recursive(yabiusername, src_dir_uri, dst_dir_uri)
        except Exception, exc:
            raise RetryException(exc, traceback.format_exc())

    def clean_up_task(self):
        # remove working directory
        self.rm(self.working_dir_uri())
        # remove local remnants directory
        shutil.rmtree(self.local_remnants_dir())


    def basename(self, path):
        return os.path.basename(path)

    def remote_to_fifo(self, uri, fifo):
        raise NotImplementedError("")

    def fifo_to_remote(self, uri, fifo):
        raise NotImplementedError("")

    def get_file(self, uri, bytes=None):
        raise NotImplementedError("")

    def rm(self, uri):
        raise NotImplementedError("")

    def mkdir(self, uri):
        raise NotImplementedError("")

    def ls(self, uri):
        raise NotImplementedError("")

    def ls_recursive(self, uri):
        raise NotImplementedError("")

    def local_copy(self, source, destination):
        raise NotImplementedError("")

    def symbolic_link(self, source, destination):
        raise NotImplementedError("")
