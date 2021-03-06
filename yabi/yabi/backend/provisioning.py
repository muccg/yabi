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

import json
from datetime import datetime
import logging
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from yabi.yabiengine.models import DynamicBackendInstance, JobDynamicBackend
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
    config_json = be.dynamic_backend_configuration.configuration
    config = _prepare_config(config_json)
    instance_handle = cloud.start_up_instance(config)

    dbinstance = _create_dynamic_backend_in_db(
        instance_handle, be, job, be_type, config_json)
    _update_backend_uri_on_job_in_db(job, be_type, dbinstance)


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


def is_instance_ready(dbinstance):
    """Is instance running and has a public IP"""
    config = _prepare_config(dbinstance.configuration)
    new_handle = cloud.is_instance_ready(dbinstance.instance_handle, config)
    if new_handle is None:
        return False

    dbinstance.instance_handle = new_handle
    dbinstance.save()

    return True


def update_dynbe_ip_addresses(job):
    for jdb in job.jobdynamicbackend_set.all():
        _fetch_and_update_ip_address(job, jdb.instance, jdb.be_type)


def destroy_backend(dbinstance):
    """
    Destroys a dynamic backend created by previously by Yabi.
    Accepts the DynamicBackendInstance that was created on BE creation.
    """
    logger.info("Destroying dynamic backend %s", dbinstance.hostname)
    config = _prepare_config(dbinstance.configuration)
    cloud.destroy_instance(dbinstance.instance_handle, config)

    dbinstance.destroyed_on = datetime.now()
    dbinstance.save()


# Implementation


def _fetch_and_update_ip_address(job, dbinstance, be_type):
    config = _prepare_config(dbinstance.configuration)
    ip_address = cloud.fetch_ip_address(dbinstance.instance_handle, config)
    dbinstance.hostname = ip_address
    dbinstance.save()
    _update_backend_uri_on_job_in_db(job, be_type, dbinstance)


def _update_backend_uri_on_job_in_db(job, be_type, db_instance):
    if be_type == 'fs':
        job.fs_backend = job.fs_credential.get_homedir_uri(db_instance.hostname)
    if be_type == 'ex':
        job.exec_backend = job.exec_credential.get_homedir_uri(db_instance.hostname)
    job.save()


def _prepare_config(config_json):
    config_dict = json.loads(config_json)

    if config_dict.get('instance_class') in ('ec2', 'ec2spot'):
        if not (settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY):
            raise ImproperlyConfigured("Please set 'AWS_ACCESS_KEY_ID' and 'AWS_SECRET_ACCESS_KEY' in your settings file.")
        config_dict.update({
            'access_id': settings.AWS_ACCESS_KEY_ID,
            'secret_key': settings.AWS_SECRET_ACCESS_KEY})

    if config_dict.get('instance_class') == 'nova':
        if not (settings.OPENSTACK_USER and settings.OPENSTACK_PASSWORD):
            raise ImproperlyConfigured("Please set 'OPENSTACK_USER' and 'OPENSTACK_PASSWORD' in your settings file.")
        config_dict.update({
            'username': settings.OPENSTACK_USER,
            'password': settings.OPENSTACK_PASSWORD})

    return config_dict


def _create_dynamic_backend_in_db(handle, be, job, be_type, config):
    dynbe_inst = DynamicBackendInstance.objects.create(
        created_for_job=job,
        configuration=config,
        instance_handle=handle)

    JobDynamicBackend.objects.create(
        job=job,
        backend=be,
        instance=dynbe_inst,
        be_type=be_type)

    return dynbe_inst
