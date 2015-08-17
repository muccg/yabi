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
from yabi.backend.fsbackend import FSBackend, pool_manager
from yabi.backend.sshexec import SSHExec
from yabi.backend.backend import fs_credential
from yabi.backend.exceptions import RetryException, FileNotFoundError
from yabi.yabiengine.urihelper import uriparse
from yabi.backend.utils import sshclient
from yabi.constants import ENVVAR_FILENAME
import paramiko
import os
import select
import errno
import stat
import traceback
import time
import logging
from itertools import dropwhile
from functools import reduce

logger = logging.getLogger(__name__)

BLOCK_SIZE = 1024

FILE_NOT_FOUND_ERR = 2


class SFTPBackend(FSBackend):
    backend_desc = "SFTP remote file system"
    backend_auth = FSBackend.SSH_AUTH

    def _sftp_copy(self, host=None, port=None, credential=None,
                   localfo=None, remotepath=None, copy=None,
                   hostkey=None, cwd=None):
        assert copy == 'put' or copy == 'get'

        status = False
        logger.debug('SFTPCopyThread {0} {1} {2}'.format(localfo.name, copy, remotepath))
        ssh = None
        sftp = None
        try:
            ssh = pool_manager.borrow(host, port, credential)
            sftp = ssh.open_sftp()
            if copy == 'put':
                sftp.putfo(localfo, remotepath, callback=None, confirm=True)
            elif copy == 'get':
                sftp.getfo(remotepath, localfo, callback=None)
            status = True

        except IOError as e:
            logger.exception("Exception in _sftp_copy")
            if e.errno == FILE_NOT_FOUND_ERR:
                raise FileNotFoundError(remotepath)

        except Exception:
            logger.exception("Exception in _sftp_copy")
        finally:
            if ssh is not None:
                if sftp is not None:
                    sftp.close()
                pool_manager.give_back(ssh, host, port, credential)
        return status

    def upload_file(self, uri, infile):
        scheme, parts = uriparse(uri)
        return self._sftp_copy(host=parts.hostname,
                               port=parts.port,
                               credential=self.cred.credential,
                               localfo=infile,
                               remotepath=parts.path,
                               copy='put',
                               hostkey=None)

    def download_file(self, uri, outfile):
        scheme, parts = uriparse(uri)
        return self._sftp_copy(host=parts.hostname,
                               port=parts.port,
                               credential=self.cred.credential,
                               localfo=outfile,
                               remotepath=parts.path,
                               copy='get',
                               hostkey=None)

    def download_dir(self, uri, outfile):
        logger.debug("SFTPBackend.download_dir: %s => tarball => %s",
                     uri, outfile)
        scheme, parts = uriparse(uri)
        executer = create_executer(self.yabiusername, uri)
        try:
            return executer.download_dir_as_tarball(parts.path, outfile)
        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

    def remote_uri_stat(self, uri):
        scheme, parts = uriparse(uri)
        remotepath = parts.path
        ssh = None
        try:
            ssh = pool_manager.borrow(parts.hostname, parts.port, self.cred.credential)
            sftp = ssh.open_sftp()

            stat = sftp.stat(remotepath)

            return {'atime': stat.st_atime, 'mtime': stat.st_mtime}

        except Exception:
            logger.exception("Exception while stating '%s'", uri)
            raise
        finally:
            if ssh is not None:
                sftp.close()
                pool_manager.give_back(ssh, parts.hostname, parts.port, self.cred.credential)

    def set_remote_uri_times(self, uri, atime, mtime):
        scheme, parts = uriparse(uri)
        remotepath = parts.path
        ssh = None
        try:
            ssh = pool_manager.borrow(parts.hostname, parts.port, self.cred.credential)
            sftp = ssh.open_sftp()

            sftp.utime(remotepath, (atime, mtime))

        except Exception:
            logger.exception("Exception while setting times for '%s'", uri)
            raise
        finally:
            if ssh is not None:
                sftp.close()
                pool_manager.give_back(ssh, parts.hostname, parts.port, self.cred.credential)

    # http://stackoverflow.com/questions/6674862/recursive-directory-download-with-paramiko
    def isdir(self, sftp, path):
        """isdir at path using sftp client"""
        try:
            return stat.S_ISDIR(sftp.stat(path).st_mode)
        except IOError:
            # Path does not exist, so by definition not a directory
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
        except FileNotFoundError:
            return {}
        except Exception as exc:
            logger.exception("ls: %s" % uri)
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
            try:
                sftp_stat_result = sftp.stat(path)
                return stat.S_ISDIR(sftp_stat_result.st_mode)
            except IOError as e:
                if e.errno == errno.ENOENT:
                    raise FileNotFoundError()

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

    def local_copy(self, src_uri, dst_uri):
        """Copy src_uri to dst_uri on the remote backend"""
        logger.debug("SFTPBackend.local_copy: %s => %s", src_uri, dst_uri)
        src_scheme, src_parts = uriparse(src_uri)
        dst_scheme, dst_parts = uriparse(dst_uri)
        logger.debug('{0} -> {1}'.format(src_uri, dst_uri))
        # Given paramiko does not support local copy, we
        # use cp on server via exec backend
        executer = create_executer(self.yabiusername, src_uri)
        try:
            executer.local_copy(src_parts.path, dst_parts.path)
        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

    def local_copy_recursive(self, src_uri, dst_uri):
        """recursively copy src_uri to dst_uri on the remote backend"""
        logger.debug("SFTPBackend.local_copy_recursive: %s => %s", src_uri, dst_uri)
        dst_scheme, dst_parts = uriparse(dst_uri)
        dst_path = dst_parts.path

        listing = self.ls(src_uri)

        executer = create_executer(self.yabiusername, src_uri)
        try:
            for key in listing:
                for listing_file in listing[key]['files']:
                    file_path = os.path.join(key, listing_file[0])
                    executer.local_copy(file_path, dst_path)
                for listing_dir in listing[key]['directories']:
                    dir_path = os.path.join(key, listing_dir[0])
                    executer.local_copy(dir_path, dst_path, recursive=True)
        except Exception as exc:
            raise RetryException(exc, traceback.format_exc())

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
    return SSHExecuter(sftp_uri, cred.credential)


class SSHExecuter(object):

    COPY_COMMAND_TEMPLATE = """
#!/bin/sh
cp -p "{0}" "{1}"
"""

    COPY_RECURSIVE_COMMAND_TEMPLATE = """
#!/bin/sh
cp -rp "{0}" "{1}"
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
                src, dest, exit_code, stderr))
        return True

    def download_dir_as_tarball(self, remotepath, outfile):
        parent_dir, target_dir = remotepath.rstrip('/').rsplit('/', 1)
        command = 'tar -cz -C "%s" "%s"' % (parent_dir, target_dir)

        logger.debug("execing command: %s" % command)

        with self.executer.sshclient() as client:
            try:
                stdin, stdout, stderr = client.exec_command(command)

                while not stdout.channel.exit_status_ready():
                    rl, wl, xl = select.select([stdout.channel], [], [])
                    if len(rl) > 0:
                        while stdout.channel.recv_ready():
                            data = stdout.channel.recv(BLOCK_SIZE)
                            outfile.write(data)

                    # Stdout might still have data, flush it all out
                    data = stdout.channel.recv(BLOCK_SIZE)
                    while data:
                        outfile.write(data)
                        data = stdout.channel.recv(BLOCK_SIZE)

                exit_status = stdout.channel.exit_status
                logger.debug("Exit status: %s", exit_status)
                if exit_status != 0:
                    raise RetryException("Exit status %s received why trying to tarball %s" % (exit_status, remotepath))
            except paramiko.SSHException as sshe:
                raise RetryException(sshe, traceback.format_exc())

        return exit_status == 0
