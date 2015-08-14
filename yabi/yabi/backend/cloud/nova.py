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

import logging
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

from .handler import LibcloudBaseHandler
from .exceptions import IncorrectConfigurationError


logger = logging.getLogger(__name__)


class NovaHandler(LibcloudBaseHandler):
    """OpenStack Nova handler."""

    MANDATORY_CONFIG_KEYS = (
        'auth_url', 'username', 'password', 'tenant', 'flavor', 'image_name', 'keypair_name')
    # In addition accepts
    # auth_version: default is '2.0_password'
    # service_type: default is 'compute'
    # service_name: ex. 'Compute Service' for Nectar
    # service_region: ex. 'Melbourne' for Nectar
    # security_group_names: ex. ["default", "ssh", "icmp"]
    # availability_zone: ex. 'tasmania' for Nectar

    def create_node(self):
        image = self._get_image_by_name(config_key='image_name')
        size = self._get_size_by_name(config_key='flavor')

        extra_args = {}
        if 'security_group_names' in self.config:
            extra_args['ex_security_groups'] = self._get_security_groups()
        if 'availability_zone' in self.config:
            extra_args['ex_availability_zone'] = self.config['availability_zone']

        node = self.driver.create_node(name=self.INSTANCE_NAME,
                                       image=image, size=size,
                                       ex_keyname=self.config['keypair_name'],
                                       **extra_args)

        return node.id

    def _create_driver(self):
        cls = get_driver(Provider.OPENSTACK)

        extra_args = {}
        extra_args.setdefault('ex_force_auth_version', '2.0_password')
        conf_to_arg = (('service_type', 'ex_force_service_type'),
                       ('service_name', 'ex_force_service_name'),
                       ('service_region', 'ex_force_service_region'))
        for conf_key, arg_name in conf_to_arg:
            if conf_key in self.config:
                extra_args[arg_name] = self.config[conf_key]

        driver = cls(self.config['username'], self.config['password'],
                     ex_force_auth_url=self.config['auth_url'],
                     ex_tenant_name=self.config['tenant'],
                     **extra_args)

        return driver

    def _get_security_groups(self):
        sg_names = self.config['security_group_names']
        all_security_groups = self.driver.ex_list_security_groups()
        our_groups = filter(lambda sg: sg.name in sg_names, all_security_groups)
        if len(sg_names) != len(our_groups):
            def quote(x):
                return "'%s'" % x
            missing = ", ".join(map(quote,
                                set(sg_names) - set(map(lambda sg: sg.name, our_groups))))
            raise IncorrectConfigurationError("Invalid security group(s): %s" % missing)

        return our_groups
