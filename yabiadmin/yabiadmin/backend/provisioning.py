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

import logging
from yabiadmin.yabiengine.models import DynamicBackendInstance, JobDynamicBackend
from datetime import datetime

from cloudseeder import InstanceHandle, InstanceConfig, CloudSeeder
import json

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
        logger.debug("%s job's %s BE not dynamic. No provisioning.", job.pk, be_type)
        return

    logger.info("Creating dynamic backend %s for job %s", be, job.pk)
    config = be.dynamic_backend_configuration
    instance = start_up_instance(config.configuration)

    create_dynamic_backend_in_db(instance, be, job, be_type, config)


def use_stagein_backend_for_execution(job):
    stagein_be = job.dynamic_backends.get(jobdynamicbackend__be_type='fs')
    JobDynamicBackend.objects.create(
        job=job,
        backend=stagein_be,
        be_type='ex')


def destroy_backend(dynbe_inst):
    """
    Destroys a dynamic backend created by previously by Yabi.
    Accepts the DynamicBackendInstance that was created on BE creation.
    """
    logger.info("Destroying dynamic backend %s", dynbe_inst.hostname)
    seeder = CloudSeeder()
    handle = InstanceHandle.from_json(dynbe_inst.instance_handle)
    instance = seeder.get_instance(handle)
    instance.destroy()

    dynbe_inst.destroyed_on = datetime.now()
    dynbe_inst.save()


# Implementation


def start_up_instance(configuration):
    config_dict = json.loads(configuration)
    config = InstanceConfig("yabi_config", config_dict)
    seeder = CloudSeeder()
    instance = seeder.instance(config)
    instance.start()

    return instance


def create_dynamic_backend_in_db(instance, be, job, be_type, config):
    dynbe_inst = DynamicBackendInstance.objects.create(
        backend=be,
        created_for_job=job,
        configuration=config,
        instance_handle=instance.handle.to_json(),
        hostname=instance.ip_address)

    JobDynamicBackend.objects.create(
        job=job,
        backend=dynbe_inst,
        be_type=be_type)
