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
import time
from libcloud.common.types import LibcloudError
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
    # region: ex. 'bparegion1'
    # 'security_group_names': [
    #       "default", "ssh", "proxied", "rdsaccess" ]

    def create_node(self):
        image = self._get_image_by_name(config_key='image_name')
        size = self._get_size_by_name(config_key='flavor')

        extra_args = {}
        if 'security_group_names' in self.config:
            extra_args['ex_securitygroups'] = self._get_security_groups()

        node = self.driver.create_node(name=self.INSTANCE_NAME,
                                       image=image, size=size,
                                       ex_keyname=self.config['keypair_name'],
                                       **extra_args)

        # Have to sleep between node creation and associating IP or with fast
        # connection I was hitting this bug:
        # https://bugs.launchpad.net/nova/+bug/1249065
        time.sleep(3)

        # TODO this again will probably have to change depending on the public IP stuff
        floating_ip = self.driver.ex_create_floating_ip()
        logger.info("Created floating ip %s", floating_ip.ip_address)
        self.driver.ex_attach_floating_ip_to_node(node, floating_ip)

        return node.id

    # TODO workarounds to test without public IPs, use super method later
    def destroy_node(self, instance_handle):
        instance_id = self._handle_to_instance_id(instance_handle)
        node = self._find_node(node_id=instance_id)
        node.destroy()
        ip = self._fetch_ip_address(instance_id)
        floating_ip = self.driver.ex_get_floating_ip(ip)
        floating_ip.delete()

    # TODO workarounds to test without public IPs, use super method later
    def fetch_ip_address(self, instance_handle):
        # instance_id = self._handle_to_instance_id(instance_handle)
        # return self._fetch_ip_address(instance_id)
        return "127.0.0.1"

    # TODO workarounds to test without public IPs, use super method later
    def _is_node_running(self, instance_id):
        TIMEOUT = 1
        node = self._find_node(node_id=instance_id)
        try:
            # We want to try just once, no retries
            # Therefore setting both wait_period and timeout to the same value
            self.driver.wait_until_running((node,), ssh_interface='private_ips',
                                           wait_period=TIMEOUT, timeout=TIMEOUT)

            return True

        except LibcloudError as e:
            if e.value.startswith('Timed out after %s seconds' % TIMEOUT):
                return False
            else:
                raise

    # TODO workarounds to test without public IPs, use super method later
    def _fetch_ip_address(self, instance_id):
        node = self._find_node(node_id=instance_id)
        if len(node.private_ips) > 1:
            return node.private_ips[1]

    def _create_driver(self):
        cls = get_driver(Provider.OPENSTACK)

        extra_args = {}
        extra_args.setdefault('ex_force_auth_version', '2.0_password')
        if 'region' in self.config:
            extra_args['ex_force_service_region'] = self.config['region']

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
            quote = lambda x: "'%s'" % x
            missing = ", ".join(map(quote,
                                set(sg_names) - set(map(lambda sg: sg.name, our_groups))))
            raise IncorrectConfigurationError("Invalid security group(s): %s" % missing)

        return our_groups
