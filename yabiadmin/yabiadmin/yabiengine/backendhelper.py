# -*- coding: utf-8 -*-
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

from django.utils import simplejson as json
import os
from yabiadmin.yabiengine.urihelper import uriparse
from yabiadmin.yabi.models import Backend, BackendCredential
from django.core.exceptions import ObjectDoesNotExist
import logging
from functools import partial


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
    bcs = BackendCredential.objects.filter(credential__user__name=yabiusername,
                                           backend__scheme=schema,
                                           credential__username=rest.username,
                                           backend__hostname=rest.hostname)

    # there must only be one valid exec credential
    if len(bcs) == 1:
        return bcs[0]

    raise ObjectDoesNotExist("Could not find backendcredential")


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
    return BackendCredential.objects.filter(credential__user__name=yabiusername,
                                            backend__scheme=schema,
                                            credential__username=username,
                                            backend__hostname=hostname)


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


def get_backend_list(yabiusername):
    """
    Returns a list of backends for user, returns in json
    """
    logger.debug('yabiusername: %s' % (yabiusername))

    results = {yabiusername: {'files': [], 'directories': []}}

    for bc in BackendCredential.objects.filter(credential__user__name=yabiusername, visible=True):
        results[yabiusername]['directories'].append([bc.homedir_uri, 0, ''])

    return json.dumps(results)
