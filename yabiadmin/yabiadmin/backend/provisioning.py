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

import json
from datetime import datetime
import logging
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from yabiadmin.yabiengine.models import DynamicBackendInstance, JobDynamicBackend
from . import cloud


logger = logging.getLogger(__name__)

# Provisioning, cleaning up Backends dynamically


def create_backend(job, be_type):
    """
    Creates the right type of BE for the job if the BE is dynamic.
    For non-dynamic BEs nothing is done.
    Creates a DynamicBackendInstance with the details of the Backend
    that has been created.
    Possible types are 'fs', and 'ex'.
    """

    if be_type == 'fs':
        be = job.tool.fs_backend
    elif be_type == 'ex':
        be = job.tool.backend
    else:
        raise ValueError('Invalid Backend type "%s"' % be_type)

    if not be.dynamic_backend:
        logger.info("%s job's %s BE not dynamic. No provisioning.", job.pk, be_type)
        return

    logger.info("Creating dynamic backend %s for job %s", be, job.pk)
    config = prepare_config(be.dynamic_backend_configuration)
    instance = cloud.start_up_instance(config)

    dbinstance = create_dynamic_backend_in_db(instance, be, job, be_type,
                                              be.dynamic_backend_configuration)
    _update_backend_uri_on_job_in_db(job, be_type, dbinstance)


def _update_backend_uri_on_job_in_db(job, be_type, db_instance):
    if be_type == 'fs':
        job.fs_backend = job.fs_credential.get_homedir_uri(db_instance.hostname)
    if be_type == 'ex':
        job.exec_backend = job.exec_credential.get_homedir_uri(db_instance.hostname)
    job.save()


def use_fs_backend_for_execution(job):
    """
    Point the EX be to the instance created for the FS BE, instead of creating
    a new instance.
    """
    fs_dbinstance = job.dynamic_backends.get(jobdynamicbackend__be_type='fs')
    JobDynamicBackend.objects.create(
        backend=job.tool.backend,
        job=job,
        instance=fs_dbinstance,
        be_type='ex')
    _update_backend_uri_on_job_in_db(job, 'ex', fs_dbinstance)


def destroy_backend(dbinstance):
    """
    Destroys a dynamic backend created by previously by Yabi.
    Accepts the DynamicBackendInstance that was created on BE creation.
    """
    logger.info("Destroying dynamic backend %s", dbinstance.hostname)
    config = prepare_config(dbinstance.configuration)
    cloud.destroy_instance(dbinstance.instance_handle, config)

    dbinstance.destroyed_on = datetime.now()
    dbinstance.save()


# Implementation


def prepare_config(dynbe_config):
    config_dict = json.loads(dynbe_config.configuration)
    if config_dict.get('instance_class') == 'ec2':
        if not (settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY):
            raise ImproperlyConfigured("Please set 'AWS_ACCESS_KEY_ID' and 'AWS_SECRET_ACCESS_KEY' in your settings file.")
        config_dict.update({
            'access_id': settings.AWS_ACCESS_KEY_ID,
            'secret_key': settings.AWS_SECRET_ACCESS_KEY})

    return config_dict


def create_dynamic_backend_in_db(instance, be, job, be_type, config):
    dynbe_inst = DynamicBackendInstance.objects.create(
        created_for_job=job,
        configuration=config,
        instance_handle=instance.handle,
        hostname=instance.ip_address)

    JobDynamicBackend.objects.create(
        job=job,
        backend=be,
        instance=dynbe_inst,
        be_type=be_type)

    return dynbe_inst
