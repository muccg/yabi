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
from functools import partial
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from yabi.yabiengine.urihelper import uriparse
from yabi.yabi.models import Backend, BackendCredential
import logging


logger = logging.getLogger(__name__)


def get_backend_by_uri(uri):
    """
    Looks up a backend object purely by uri. Ignored username. Thus diesnt consider credentials.
    Just pure hostname/portnumber. Used by HostKey system for find what hostkeys are allowed
    """
    schema, rest = uriparse(uri)
    netloc = rest.netloc
    if ':' in netloc:
        host, port = netloc.split(':')
    else:
        host, port = netloc, None

    return Backend.objects.filter(scheme=schema, hostname=host, port=port)


def get_hostkeys_by_uri(uri):
    return Backend.objects.filter(backend__in=get_backend_by_uri(uri))


def get_exec_backendcredential_for_uri(yabiusername, uri):
    """
    Looks up a backend credential based on the supplied uri, which should include a username.
    Returns bc, will log and reraise ObjectDoesNotExist and MultipleObjectsReturned exceptions if more than one credential
    """
    logger.debug('yabiusername: %s uri: %s' % (yabiusername, uri))

    # parse the URI into chunks
    schema, rest = uriparse(uri)

    # enforce Exec scehmas only
    from ..backend import ExecBackend
    if not ExecBackend.get_backend_cls_for_scheme(schema):
        logger.error("get_exec_backendcredential_for_uri was asked to get an fs schema! This is forbidden.")
        raise ValueError("Invalid schema in uri passed to get_exec_backendcredential_for_uri: asked for %s" % schema)

    path = rest.path
    if path != "/":
        logger.error("get_exec_backendcredential_for_uri was passed a uri with a path! This is forbidden. Path must be / for exec backends")
        raise ValueError("Invalid path in uri passed to get_exec_backendcredential_for_uri: path passed in was: %s" % path)

    # get our set of credential candidates
    bcs = _get_credential_candidates(yabiusername, schema, rest.username, rest.hostname)

    if len(bcs) == 0:
        raise ObjectDoesNotExist("Could not find backendcredential")

    return bcs[0]


def _enforce_FS_schema_only(schema):
    from ..backend import FSBackend
    if not FSBackend.get_backend_cls_for_scheme(schema):
        logger.error("get_fs_backendcredential_for_uri was asked to get an executions schema! This is forbidden.")
        raise ValueError("Invalid schema in uri passed to get_fs_backendcredential_for_uri: schema passed in was %s" % schema)


def _normalise_path(path):
    new_path = os.path.normpath(path)  # normalise path to get rid of ../../ style exploits
    new_path = path.rstrip('/')  # and ignore trailing slashes
    return new_path


def _get_credential_candidates(yabiusername, schema, username, hostname):
    def is_running_dyn_be(hostname):
        return (Q(backend__jobdynamicbackend__instance__hostname=hostname) &
                Q(backend__jobdynamicbackend__instance__destroyed_on__isnull=True))

    def is_hostname_matching(hostname):
        return Q(backend__hostname=hostname) | is_running_dyn_be(hostname)

    return BackendCredential.objects.filter(
        credential__user__name=yabiusername,
        backend__scheme=schema,
        credential__username=username).filter(is_hostname_matching(hostname))


def _be_cred_path(be_cred):
    return os.path.join(be_cred.backend.path, be_cred.homedir).rstrip('/')


def _does_path_match_be_cred(path, be_cred):
    return path.startswith(_be_cred_path(be_cred))


def _find_be_cred_with_longest_path(be_creds):
    if len(be_creds) > 0:
        return sorted(be_creds, key=lambda x: -len(_be_cred_path(x)))[0]


def get_fs_backendcredential_for_uri(yabiusername, uri):
    """
    Looks up a backend credential based on the supplied uri, which should include a username.
    Returns bc, will log and reraise ObjectDoesNotExist and MultipleObjectsReturned exceptions if more than one credential
    """
    logger.debug('yabiusername: %s uri: %s' % (yabiusername, uri))

    schema, rest = uriparse(uri)

    _enforce_FS_schema_only(schema)
    path = _normalise_path(rest.path)

    bc_candidates = _get_credential_candidates(yabiusername, schema, rest.username, rest.hostname)
    logger.debug("credentials candidates [%s]" % (",".join([str(x) for x in bc_candidates])))

    matches_path = partial(_does_path_match_be_cred, path)
    matching_bcs = filter(matches_path, bc_candidates)
    if len(matching_bcs) == 0:
        raise ObjectDoesNotExist("Could not find backendcredential")

    cred = _find_be_cred_with_longest_path(matching_bcs)

    logger.info("chose cred {0} {1} {2}".format(cred.id, cred.backend.path, cred.homedir))

    return cred


def get_fs_credential_for_uri(yabiusername, uri):
    return get_fs_backendcredential_for_uri(yabiusername, uri).credential


def get_fs_backend_for_uri(yabiusername, uri):
    return get_fs_backendcredential_for_uri(yabiusername, uri).backend


def get_exec_credential_for_uri(yabiusername, uri):
    return get_exec_backendcredential_for_uri(yabiusername, uri).credential


def get_exec_backend_for_uri(yabiusername, uri):
    return get_exec_backendcredential_for_uri(yabiusername, uri).backend
