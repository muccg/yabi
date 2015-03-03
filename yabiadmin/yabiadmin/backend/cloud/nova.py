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
