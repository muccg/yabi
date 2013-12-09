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
from yabiadmin.backend.sshexec import SSHExec
from yabiadmin.backend.backend import fs_credential
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.yabiengine.urihelper import uriparse
from yabiadmin.backend.utils import sshclient
from yabiadmin.constants import ENVVAR_FILENAME
import os
import errno
import stat
import traceback
import time
import logging
import threading
from itertools import dropwhile
from functools import reduce

logger = logging.getLogger(__name__)


class SFTPCopyThread(threading.Thread):

    def __init__(self, host=None, port=None, credential=None, localpath=None, remotepath=None, copy=None, hostkey=None, purge=None, queue=None, cwd=None):
        threading.Thread.__init__(self)
        self.hostname = host
        self.port = port
        self.credential = credential
        self.localpath = localpath
        self.remotepath = remotepath
        self.copy = copy
        self.hostkey = hostkey
        self.purge = purge
        self.queue = queue
        self.cwd = cwd
        assert copy == 'put' or copy == 'get'

    def run(self):
        status = -1
        logger.debug('SFTPCopyThread {0} {1} {2}'.format(self.localpath, self.copy, self.remotepath))
        try:
            logger.debug('SFTPCopyThread start copy')
            ssh = sshclient(self.hostname, self.port, self.credential)
            sftp = ssh.open_sftp()
            if self.copy == 'put':
                sftp.put(self.localpath, self.remotepath, callback=None, confirm=True)
            elif self.copy == 'get':
                try:
                    sftp.get(self.remotepath, self.localpath, callback=None)
                # bogus error because stat of fifo returns 0
                except IOError as ioerr:
                    msg = str(ioerr)
                    if msg.startswith("size mismatch in get!  0 !="):
                        status = 0
                    else:
                        raise

            status = 0

        except Exception as exc:
            logger.error(traceback.format_exc())
            logger.error(exc)
        finally:
            if ssh is not None:
                ssh.close()
            if self.queue is not None:
                self.queue.put(status)
            if self.purge is not None and os.path.exists(self.purge):
                #os.unlink(self.purge)
                # commented out above as it caused stage out to fail
                pass


class SFTPBackend(FSBackend):

    def fifo_to_remote(self, uri, fifo, queue=None):
        """initiate a copy from local fifo to uri"""
        scheme, parts = uriparse(uri)
        assert os.path.exists(fifo)
        thread = SFTPCopyThread(host=parts.hostname,
                                port=parts.port,
                                credential=self.cred.credential,
                                localpath=fifo,
                                remotepath=parts.path,
                                copy='put',
                                hostkey=None,
                                purge=fifo,
                                queue=queue)
        thread.start()
        return thread

    def remote_to_fifo(self, uri, fifo, queue=None):
        """initiate a copy from remote file to fifo"""
        scheme, parts = uriparse(uri)
        assert os.path.exists(fifo)
        # don't think we should purge fifo after writing, rather after reading completes
        thread = SFTPCopyThread(host=parts.hostname,
                                port=parts.port,
                                credential=self.cred.credential,
                                localpath=fifo,
                                remotepath=parts.path,
                                copy='get',
                                hostkey=None,
                                purge=None,
                                queue=queue)
        thread.start()
        return thread

    # http://stackoverflow.com/questions/6674862/recursive-directory-download-with-paramiko
    def isdir(self, sftp, path):
        """isdir at path using sftp client"""
        try:
            return stat.S_ISDIR(sftp.stat(path).st_mode)
        except IOError:
            #Path does not exist, so by definition not a directory
            return False

    def path_exists(self, sftp, path):
        try:
            sftp.stat(path)
            return True
        except IOError as e:
            if e.errno == errno.ENOENT:  # No such file or directory
                return False
            else:
                raise

    def mkdir(self, uri):
        """mkdir at uri"""
        self.set_cred(uri)
        scheme, parts = uriparse(uri)
        path = parts.path
        ssh = sshclient(parts.hostname, parts.port, self.cred.credential)
        try:
            sftp = ssh.open_sftp()
            try:
                self._rm(sftp, path)
                logger.debug("deleted existing directory %s OK" % path)
            except Exception as ex:
                logger.debug("could not remove directory %s: %s" % (path, ex))

            def full_path(result, d):
                previous = result[-1] if result else ""
                result.append("%s/%s" % (previous, d))
                return result

            dirs = [p for p in path.split("/") if p.strip() != '']
            dir_full_paths = reduce(full_path, dirs, [])
            non_existant_dirs = dropwhile(
                lambda d: self.path_exists(sftp, d), dir_full_paths)

            for d in non_existant_dirs:
                sftp.mkdir(d)

            logger.debug("created dir %s OK" % path)

        except Exception as exc:
            logger.error(exc)
            raise RetryException(exc, traceback.format_exc())
        finally:
            try:
                if ssh is not None:
                    ssh.close()
            except:
                pass

    def ls(self, uri):
        """ls at uri"""
        self.set_cred(uri)
        scheme, parts = uriparse(uri)
        ssh = sshclient(parts.hostname, parts.port, self.cred.credential)
        try:
            sftp = ssh.open_sftp()
            results = self._do_ls(sftp, parts.path)
            output = {}
            output[parts.path] = results
            return output
        except Exception as exc:
            logger.error(exc)
            raise RetryException(exc, traceback.format_exc())
        finally:
            try:
                if ssh is not None:
                    ssh.close()
            except:
                pass

    def _do_ls(self, sftp, path):
        """do an ls using sftp client at path"""

        def is_dir(path):
            import stat
            sftp_stat_result = sftp.stat(path)
            return stat.S_ISDIR(sftp_stat_result.st_mode)

        if is_dir(path):
            dirs, files = self._do_ls_dir(sftp, path)
        else:
            dirs = []
            file_ls = self._do_ls_file(sftp, path)
            files = [file_ls]

        dirs.sort()
        files.sort()
        return {
            "directories": dirs,
            "files": files
        }

    def _format_stat_entry(self, entry, filename=None):
        filename = filename or entry.filename
        return [filename, entry.st_size, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(entry.st_mtime)), stat.S_ISLNK(entry.st_mode)]

    def _do_ls_file(self, sftp, path):
        filename = os.path.basename(path)
        entry = sftp.stat(path)
        return self._format_stat_entry(entry, filename=filename)

    def _do_ls_dir(self, sftp, path):
        dirs = []
        files = []
        format = self._format_stat_entry

        for entry in sftp.listdir_attr(path):
            if entry.filename.startswith('.') and entry.filename != ENVVAR_FILENAME:
                continue

            if stat.S_ISDIR(entry.st_mode):  # dir
                dirs.append(format(entry))
            elif stat.S_ISLNK(entry.st_mode):  # symlink
                full_path = os.path.join(path, entry.filename)
                try:
                    target = sftp.stat(full_path)
                except IOError:
                    logger.warning('Broken symlink "%s"', full_path)
                else:
                    if stat.S_ISDIR(target.st_mode):
                        dirs.append(format(entry))
                    else:
                        files.append(format(entry))
            else:  # file
                files.append(format(entry))

        return dirs, files

    def local_copy(self, src_uri, dst_uri, recursive=False):
        """Copy src_uri to dst_uri on the remote backend"""
        logger.debug("SFTPBackend.local_copy(recursive=%s): %s => %s",
                     recursive, src_uri, dst_uri)
        src_scheme, src_parts = uriparse(src_uri)
        dst_scheme, dst_parts = uriparse(dst_uri)
        logger.debug('{0} -> {1}'.format(src_uri, dst_uri))
        # Given paramiko does not support local copy, we
        # use cp on server via exec backend
        executer = create_executer(self.yabiusername, src_uri)
        try:
            executer.local_copy(src_parts.path, dst_parts.path, recursive)
        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

    def local_copy_recursive(self, src_uri, dst_uri):
        """recursively copy src_uri to dst_uri on the remote backend"""
        self.local_copy(src_uri, dst_uri, recursive=True)

    def symbolic_link(self, src_uri, dst_uri):
        """symbolic link to target_uri called link_uri."""
        logger.debug("SFTPBackend.symbolic_link: %s => %s",
                     src_uri, dst_uri)
        src_scheme, src_parts = uriparse(src_uri)
        dst_scheme, dst_parts = uriparse(dst_uri)
        logger.debug('{0} -> {1}'.format(src_uri, dst_uri))

        executer = create_executer(self.yabiusername, src_uri)
        try:
            executer.local_symlink(src_parts.path, dst_parts.path)
        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

    def rm(self, uri):
        """recursively delete a uri"""
        scheme, parts = uriparse(uri)
        logger.debug('{0}'.format(parts.path))
        ssh = sshclient(parts.hostname, parts.port, self.cred.credential)
        try:
            sftp = ssh.open_sftp()
            self._rm(sftp, parts.path)
        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())
        finally:
            try:
                if ssh is not None:
                    ssh.close()
            except:
                pass

    def _rm(self, sftp, path):
        """recursively delete a dir or file using sftp client"""
        if self.isdir(sftp, path):
            for filename in sftp.listdir(path):
                filepath = os.path.join(path, filename)
                self._rm(sftp, filepath)
            sftp.rmdir(path)
        else:
            sftp.remove(path)


def create_executer(yabiusername, sftp_uri):
    cred = fs_credential(yabiusername, sftp_uri)
    return SSHLocalCopyAndLinkExecuter(sftp_uri, cred.credential)


class SSHLocalCopyAndLinkExecuter(object):

    COPY_COMMAND_TEMPLATE = """
#!/bin/sh
cp "{0}" "{1}"
"""

    COPY_RECURSIVE_COMMAND_TEMPLATE = """
#!/bin/sh
cp -r "{0}/"* "{1}"
"""

    SYMLINK_COMMAND_TEMPLATE = """
#!/bin/sh
ln -s "{0}" "{1}"
"""

    def __init__(self, uri, credential):
        self.executer = SSHExec(uri, credential)

    def local_copy(self, src, dest, recursive=False):
        logger.debug('SSH Local Copy %s => %s', src, dest)
        if recursive:
            cmd = self.COPY_RECURSIVE_COMMAND_TEMPLATE.format(src, dest)
        else:
            cmd = self.COPY_COMMAND_TEMPLATE.format(src, dest)
        exit_code, stdout, stderr = self.executer.exec_script(cmd)
        if exit_code > 0 or stderr:
            raise RuntimeError("Couldn't (recursive=%s) copy %s to %s. Exit code: %s. STDERR:\n%s" % (
                recursive, src, dest, exit_code, stderr))
        return True

    def local_symlink(self, src, dest):
        logger.debug('SSH Local Symlink %s => %s', src, dest)
        cmd = self.SYMLINK_COMMAND_TEMPLATE.format(src, dest)
        exit_code, stdout, stderr = self.executer.exec_script(cmd)
        if exit_code > 0 or stderr:
            raise RuntimeError("Couldn't symlink %s to %s. Exit code: %s. STDERR:\n%s" % (
                src, dest, exit_code, stderr()))
        return True
