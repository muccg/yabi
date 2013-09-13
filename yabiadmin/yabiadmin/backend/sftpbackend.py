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
from yabiadmin.backend.execbackend import ExecBackend
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.backend.parsers import parse_ls
from yabiadmin.yabiengine.urihelper import uriparse
from yabiadmin.backend.utils import sshclient
import os
import errno
import shutil
import stat
import paramiko
import traceback
import time
import logging
import threading
import Queue
from itertools import dropwhile

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
        transport = None
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
                except IOError, ioerr:
                    msg = str(ioerr)
                    if msg.startswith("size mismatch in get!  0 !="):
                        status = 0
                    else:
                        raise

            status = 0

        except Exception, exc:
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
        assert  os.path.exists(fifo)
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
        except IOError, e:
            if e.errno == errno.ENOENT: # No such file or directory
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
            except Exception,ex:
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

        except Exception, exc:
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
        except Exception, exc:
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
        results = {"files": [], "directories": []}
        def is_dir(path):
            import stat
            sftp_stat_result = sftp.stat(path)
            return stat.S_ISDIR(sftp_stat_result.st_mode)

        if not is_dir(path):
            filename = os.path.basename(path)
            entry = sftp.stat(path)
            results['files'].append([filename, entry.st_size, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(entry.st_mtime)), stat.S_ISLNK(entry.st_mode)])
            return results

        for entry in sftp.listdir_attr(path):
            # if not a hidden directory
            if not entry.filename.startswith('.'):
                s = sftp.stat(os.path.join(path, entry.filename))            # stat the destination of any link
                if stat.S_ISDIR(s.st_mode):
                    # directory
                    results['directories'].append([entry.filename, entry.st_size, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(entry.st_mtime)), stat.S_ISLNK(entry.st_mode)])
                else:
                    # file or symlink to directory
                    results['files'].append([entry.filename, entry.st_size, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(entry.st_mtime)), stat.S_ISLNK(entry.st_mode)])

        # sort entries
        results['directories'].sort()
        results['files'].sort()

        return results

    def ls_recursive(self, uri):
        """recursively ls at uri"""
        self.set_cred(uri)
        scheme, parts = uriparse(uri)
        output = {"files": [], "directories": []}
        ssh = sshclient(parts.hostname, parts.port, self.cred.credential)
        try:
            sftp = ssh.open_sftp()
            output = self._do_stat(sftp, parts.path) or self._do_ls_r(sftp, parts.path, {})
        except Exception, exc:
            logger.error(exc)
            raise RetryException(exc, traceback.format_exc())
        finally:
            try:
                if ssh is not None:
                    ssh.close()
            except:
                pass

        return output

    def _do_ls_r(self, sftp, path, output):
        """recursively do an ls"""
        try:
            results = self._do_ls(sftp, path)
        except IOError, ioe:
            logger.warning(ioe)
            # permissions...
            return output
        output[path] = results

        for filename, size, date, link in results['directories']:
            self._do_ls_r(sftp, os.path.join(path, filename), output)

        return output

    def _do_stat(self, sftp, path):
        """stat a path using sftp client"""
        try:
            lresult = sftp.lstat(path)
        except IOError, ioe:
            logger.error("%s: path = %s" % (ioe, path))
            raise

        result = sftp.stat(path)
        if stat.S_ISREG(result.st_mode):
            # regular file
            output = {
                'directories': [],
                'files': [
                    [path.rsplit('/', 1)[-1], lresult.st_size, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(lresult.st_mtime)), stat.S_ISLNK(lresult.st_mode)]
                ]
            }

            return {path: output}
        return None

    def local_copy(self, src_uri, dst_uri):
        """Copy src_uri to dst_uri on the remote backend"""
        logger.debug("SFTPBackend.local_copy: %s => %s" % (src_uri, dst_uri))
        src_scheme, src_parts = uriparse(src_uri)
        dst_scheme, dst_parts = uriparse(dst_uri)
        logger.debug('{0} -> {1}'.format(src_uri, dst_uri))
        assert False, "TODO review whether we need this, we want to do it this way etc."
        # Given paramiko does not support local copy, we
        # use cp on server via exec backend
        ex_backend = ExecBackend.factory(self.task)
        try:
            ex_backend.local_copy(src_parts.path,dst_parts.path)
        except Exception, exc:
            raise RetryException(exc, traceback.format_exc())

    def local_copy_recursive(self, src_uri, dst_uri):
        """recursively copy src_uri to dst_uri on the remote backend"""
        logger.debug("SFTPBackend.local_copy_recursive: %s => %s" % (src_uri, dst_uri))
        assert False, "TODO"

        src_scheme, src_parts = uriparse(src_uri)
        dst_scheme, dst_parts = uriparse(dst_uri)
        logger.debug('{0} -> {1}'.format(src_uri, dst_uri))
        try:
            shutil.copytree(src_parts.path, dst_parts.path)
        except Exception, exc:
            raise RetryException(exc, traceback.format_exc())

    def symbolic_link(self, target_uri, link_uri):
        """symbolic link to target_uri called link_uri."""
        logger.debug('{0}'.format(parts.path))
        target_scheme, target_parts = uriparse(target_uri)
        link_scheme, link_parts = uriparse(link_uri)
        ssh = None
        try:
            ssh = sshclient(target_parts.hostname, target_parts.port, self.cred.credential)
            sftp = ssh.open_sftp()
            sftp.symlink(target_parts.path, link_parts.path)
        except Exception, exc:
            raise RetryException(exc, traceback.format_exc())
        finally:
            try:
                if ssh is not None:
                    ssh.close()
            except:
                pass

    def rm(self, uri):
        """recursively delete a uri"""
        scheme, parts = uriparse(uri)
        logger.debug('{0}'.format(parts.path))
        ssh = sshclient(parts.hostname, parts.port, self.cred.credential)
        try:
            sftp = ssh.open_sftp()
            self._rm(sftp, parts.path)
        except Exception, exc:
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

    def set_cred(self, uri):
        from yabiadmin.backend.backend import fs_credential
        self.cred = fs_credential(self.yabiusername, uri)
