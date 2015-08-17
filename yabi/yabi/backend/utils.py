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

import os
import datetime
import subprocess
import socket
import string
import threading
import traceback
from mako.template import Template
import paramiko
import logging
from yabi.backend.exceptions import RetryException
import uuid
import StringIO
from functools import partial
from itertools import tee, ifilter, ifilterfalse
logger = logging.getLogger(__name__)


def execute(args, bufsize=0, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, cwd=None, env=None):
    """execute a process and return a handle to the process"""
    try:
        logger.debug(args)
        process = subprocess.Popen(args, bufsize=bufsize, stdin=stdin, stdout=stdout, stderr=stderr, shell=shell, cwd=cwd, env=env)
    except Exception as exc:
        logger.error(exc)
        raise RetryException(exc, traceback.format_exc())

    return process


def blocking_execute(args, bufsize=0, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, cwd=None, env=None, report_pid_callback=(lambda x: None)):
    """execute a process and wait for it to end"""
    status = None
    try:
        logger.debug(args)
        logger.debug(cwd)
        process = execute(args, bufsize=bufsize, stdin=stdin, stdout=stdout, stderr=stderr, shell=shell, cwd=cwd, env=env)
        report_pid_callback(process.pid)
        stdout_data, stderr_data = process.communicate(stdin)
        status = process.returncode

    except Exception as exc:
        logger.error('execute failed {0}'.format(status))
        from yabi.backend.exceptions import RetryException
        raise RetryException(exc, traceback.format_exc())

    return status


def valid_filename(filename):
    """Ensure filenames for fifo are valid, trimmed to 100"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    filename = filename[:100]
    return filename


def create_fifo(suffix='', dir='/tmp'):
    """make a fifo on the filesystem and return its path"""
    filename = 'yabi_fifo_' + str(uuid.uuid4()) + '_' + suffix
    filename = valid_filename(filename)
    filename = os.path.join(dir, filename)
    filename = str(filename)
    logger.debug('create_fifo {0}'.format(filename))
    os.umask(0)
    os.mkfifo(filename, 0o600)
    return filename


def submission_script(template, working, command, modules, cpus, memory, walltime, yabiusername, username, host, queue, tasknum, tasktotal, envvars):
    """Mako templating support function for submission script templating."""
    cleaned_template = template.replace('\r\n', '\n').replace('\n\r', '\n').replace('\r', '\n')
    tmpl = Template(cleaned_template)

    # our variable space
    variables = {
        'working': working,
        'command': command,
        'modules': [string.strip(m) for m in modules.split(",") if string.strip(m)] if modules else [],
        'cpus': cpus,
        'memory': memory,
        'walltime': walltime,
        'yabiusername': yabiusername,
        'username': username,
        'host': host,
        'queue': queue,
        'tasknum': tasknum,
        'tasktotal': tasktotal,
        'envvars': envvars,
    }

    return tmpl.render_unicode(**variables)


def get_host_key(hostname):
    """
    host key for hostname. Does not handle multiple keys for the same host
    Not being used. I dont think it worth implementing until Paramiko supports ECDSA keys
    """
    logger.debug('get_host_key {0}'.format(hostname))
    from yabi.yabi.models import HostKey
    host_keys = HostKey.objects.filter(hostname=hostname).filter(allowed=True)
    for key in host_keys:
        logger.debug('{0} {1}'.format(key.key_type, key.data))
        return key.key_type, key.data
    return None, None


def harvest_host_key(hostname, port, username, password, pkey):
    """
    Attempt an ssh connection and extract the host key. Does not raise errors.
    Not being used. I dont think it worth implementing until Paramiko supports ECDSA keys
    """
    logger.debug('save_host_key {0}'.format(hostname))
    try:
        # connect to harvest the host key
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            pkey=pkey,
            key_filename=None,
            timeout=None,
            allow_agent=False,
            look_for_keys=True,
            compress=False,
            sock=None)

        keys = ssh.get_host_keys()
        logger.debug(keys.lookup(hostname))
        key_dict = keys.lookup(hostname)
        if key_dict is None:
            logger.error('No host key found for {0}'.format(hostname))
            return

        # process any host keys
        import binascii
        for key_type in key_dict.keys():
            fingerprint = binascii.hexlify(key_dict[key_type].get_fingerprint())
            data = key_dict[key_type].get_base64()
            logger.debug('{0} {1}'.format(fingerprint, data))

            # dont save duplicate entries
            from yabi.yabi.models import HostKey
            if HostKey.objects.filter(hostname=hostname, key_type=key_type, fingerprint=fingerprint, data=data).count() == 1:
                continue

            # save the key
            host_key = HostKey.objects.create(hostname=hostname, fingerprint=fingerprint, key_type=key_type, data=data)
            host_key.save()
    except Exception as exc:
        logger.error(exc)


def try_to_load_key_file(key_type, credential_key, passphrase=None):
    try:
        pkey = key_type.from_private_key(StringIO.StringIO(credential_key), passphrase)
        return pkey
    except paramiko.SSHException as sshex:
        # ignoring exceptions of form "not a valid (DSA|RSA) private key file"
        msg = str(sshex)
        if not (msg.startswith("not a valid") and msg.endswith("private key file")):
            logger.exception("SSHException caught:")
            raise

    return None


def create_paramiko_pkey(key, passphrase=None):
    if passphrase == "":
        passphrase = None
    pkey = (
        try_to_load_key_file(paramiko.RSAKey, key, passphrase) or
        try_to_load_key_file(paramiko.DSSKey, key, passphrase))

    if pkey is None:
        raise paramiko.SSHException("Passed in key not supported. Supported keys are RSA and DSS")

    return pkey


def sshclient(hostname, port, credential):
    if port is None:
        port = 22
    ssh = None

    c = credential.get_decrypted()

    logger.debug('Connecting to {0}@{1}:{2}'.format(c.username, hostname, port))

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()

        connect = partial(ssh.connect,
                          hostname=hostname,
                          port=port,
                          username=c.username,
                          key_filename=None,
                          timeout=None,
                          allow_agent=False,
                          look_for_keys=False,
                          compress=False,
                          sock=None)

        if c.key:
            private_key = create_paramiko_pkey(c.key, c.password)
            connect(pkey=private_key)
        else:
            logger.debug("Connecting using password")
            connect(password=c.password)

    except paramiko.BadHostKeyException as bhke:  # BadHostKeyException - if the server's host key could not be verified
        raise RetryException(bhke, traceback.format_exc())
    except paramiko.AuthenticationException as aue:  # AuthenticationException - if authentication failed
        raise RetryException(aue, traceback.format_exc())
    except paramiko.SSHException as sshe:  # SSHException - if there was any other error connecting or establishing an SSH session
        raise RetryException(sshe, traceback.format_exc())
    except socket.error as soe:  # socket.error - if a socket error occurred while connecting
        raise RetryException(soe, traceback.format_exc())

    return ssh


def _get_creation_date(file_path):
    """
    @param file_path:
    @return: Creation date as a string in format like "Jul 26 2013"
    """
    return datetime.datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%b %d %Y")


def ls(top_level_path, recurse=False):
    listing = {}

    def append_slash(path):
        if not path.endswith("/"):
            return path + "/"
        else:
            return path

    def info_tuple(root, name):
        file_path = os.path.join(root, name)
        is_a_link = os.path.islink(file_path)
        if is_a_link:
            size = os.lstat(file_path).st_size
        else:
            size = os.path.getsize(file_path)
        date_string = _get_creation_date(file_path)

        return name, size, date_string, is_a_link

    if os.path.isfile(top_level_path):
        parent_folder = os.path.dirname(top_level_path)
        file_name = os.path.basename(top_level_path)
        file_info = info_tuple(parent_folder, file_name)
        return {top_level_path: {"files": [file_info], "directories": []}}

    for root, directories, files in os.walk(top_level_path, topdown=True):
        slashed_root = append_slash(root)
        listing[slashed_root] = {}
        listing[slashed_root]['files'] = []
        for file_name in sorted(files):
                file_info_tuple = info_tuple(root, file_name)
                listing[slashed_root]['files'].append(file_info_tuple)

        listing[slashed_root]['directories'] = []
        for directory in sorted(directories):
            directory_info_tuple = info_tuple(root, directory)
            listing[slashed_root]['directories'].append(directory_info_tuple)

        if root == top_level_path and not recurse:
            return listing

    return listing


def partition(pred, iterable):
    """Partition an iterable in two iterable based on the predicate"""
    t1, t2 = tee(iterable)
    return ifilter(pred, t1), ifilterfalse(pred, t2)


class SaveExceptionThread(threading.Thread):
    """A thread that saves an exception raised during its execution.

       The exception is saved into the exception property."""
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        self.exception = None

        def wrapped_target(*args, **kwargs):
            try:
                return target(*args, **kwargs)
            except Exception as e:
                self.exception = e
                raise e

        threading.Thread.__init__(self, group, wrapped_target, name, args, kwargs)
