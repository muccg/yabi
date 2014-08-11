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
import os
import logging
from collections import namedtuple
logger = logging.getLogger(__name__)


"""
The api we expose to celery tasks and yabi to interact with file/exec backends
"""


DirEntry = namedtuple("DirEntry", ("uri", "size", "is_symlink"))
FileEntry = namedtuple("FileEntry", ("filename", "size", "date", "link"))


def put_file(yabiusername, filename, uri):
    """
    Put a file to a backend by streaming through a fifo.
    Returns the opened fifo for the upload to write to
    """
    from yabiadmin.backend.fsbackend import FSBackend
    return FSBackend.remote_file_upload(yabiusername, filename, uri)


def get_file(yabiusername, uri):
    """Get a file from a backend"""
    from yabiadmin.backend.fsbackend import FSBackend
    return FSBackend.remote_file_download(yabiusername, uri)


def get_zipped_dir(yabiusername, uri):
    from yabiadmin.backend.fsbackend import FSBackend
    return FSBackend.remote_file_download(yabiusername, uri, is_dir=True)


def copy_file(yabiusername, src_uri, dst_uri):
    """Remote copy a file between two backends"""
    from yabiadmin.backend.fsbackend import FSBackend
    FSBackend.remote_file_copy(yabiusername, src_uri, dst_uri)


def rcopy_file(yabiusername, src_uri, dst_uri):
    """Remote copy between two backends"""
    from yabiadmin.backend.fsbackend import FSBackend
    FSBackend.remote_copy(yabiusername, src_uri, dst_uri)


def rm_file(yabiusername, uri):
    """rm at the given uri"""
    from yabiadmin.backend.fsbackend import FSBackend
    backend = FSBackend.urifactory(yabiusername, uri)
    return backend.rm(uri)


def mkdir(yabiusername, uri):
    """Make a directory at the given uri"""
    from yabiadmin.backend.fsbackend import FSBackend
    backend = FSBackend.urifactory(yabiusername, uri)
    return backend.mkdir(uri)


def get_listing(yabiusername, uri, recurse=False):
    """Get a file listing. Used in front end file manager."""
    from yabiadmin.backend.fsbackend import FSBackend
    backend = FSBackend.urifactory(yabiusername, uri)
    if recurse is True:
        return backend.ls_recursive(uri)
    else:
        return backend.ls(uri)


def get_file_list(yabiusername, uri, recurse=False):
    """
    Get a file list and return a bespoke structure
    Used by legacy code in yabiengine to determine dependencies for tasks
    """

    results = get_listing(yabiusername, uri, recurse)

    # determine the length of the common prefix of keys
    spl = min(map(len, results))

    file_list = []
    for key, item in results.iteritems():
        for entry in item["files"]:
            listing = (os.path.join(key[spl:], entry[0]),) + tuple(entry[1:])
            file_list.append(listing)
    return [FileEntry(*entry) for entry in file_list]


def get_backend_list(yabiusername):
    """Returns a list of backends for user, returns in json"""
    from yabiadmin.yabi.models import BackendCredential

    def becred_as_dir_entry(bc):
        return DirEntry(uri=bc.homedir_uri, size=0, is_symlink=False)

    visible_becreds = BackendCredential.objects.filter(
        backend__dynamic_backend=False,
        credential__user__name=yabiusername,
        visible=True)
    dir_entries = map(becred_as_dir_entry, visible_becreds)

    return {
        yabiusername: {
            'files': [],
            'directories': dir_entries}}


def stage_in_files(task):
    """Stage in files for a task"""
    from yabiadmin.backend.fsbackend import FSBackend
    backend = FSBackend.factory(task)
    backend.stage_in_files()


def submit_task(task):
    """Submit a task"""
    from yabiadmin.backend.execbackend import ExecBackend
    backend = ExecBackend.factory(task)
    backend.submit_task()


def poll_task_status(task):
    """Poll the status of a task. Will raise a retry exception until complete."""
    from yabiadmin.backend.execbackend import ExecBackend
    backend = ExecBackend.factory(task)
    backend.poll_task_status()


def stage_out_files(task):
    """Stage out files for a task"""
    from yabiadmin.backend.fsbackend import FSBackend
    backend = FSBackend.factory(task)
    backend.stage_out_files()


def clean_up_task(task):
    """Clean up after a task"""
    from yabiadmin.backend.fsbackend import FSBackend
    backend = FSBackend.factory(task)
    backend.clean_up_task()


def abort_task(task):
    """Try to abort a running task"""
    from yabiadmin.backend.execbackend import ExecBackend
    backend = ExecBackend.factory(task)
    backend.abort_task()


def exec_credential(yabiusername, uri):
    """
    Return a exec_credential for a given user and uri
    Currently wraps legacy code in backendhelper
    raises ObjectDoesNotExist, DecryptedCredentialNotAvailable
    """
    from yabiadmin.yabiengine import backendhelper
    return backendhelper.get_exec_backendcredential_for_uri(yabiusername, uri)


def fs_credential(yabiusername, uri):
    """
    Return a fs_credential for a given user and uri
    Currently wraps legacy code in backendhelper
    raises ObjectDoesNotExist, DecryptedCredentialNotAvailable
    """
    from yabiadmin.yabiengine import backendhelper
    return backendhelper.get_fs_backendcredential_for_uri(yabiusername, uri)
