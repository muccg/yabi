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
from functools import partial
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from .exceptions import IncorrectConfigurationError


logger = logging.getLogger(__name__)


# TODO this is a copy of ec2.py, implement, DRY etc.

# TODO We can probably move away from having an instance
# Just return handle and work with the handle
# Add a service method for getting the IP to the Handler
class CloudInstance(object):
    def __init__(self, node_id, ip_addresses):
        self.node_id = node_id
        self.ip_addresses = ip_addresses

    @property
    def handle(self):
        return self.node_id

    @property
    def ip_address(self):
        if len(self.ip_addresses) > 0:
            return self.ip_addresses[0]


class EC2SpotHandler(object):
    MANDATORY_CONFIG_KEYS = (
        'access_id', 'secret_key', 'region', 'size_id', 'ami_id', 'keypair_name')
    # In addition accepts
    # 'security_group_names': [
    #       "default", "ssh", "proxied", "rdsaccess" ]

    _ec2_attrs = filter(lambda x: x.startswith('EC2'), dir(Provider))
    VALID_REGIONS = map(partial(getattr, Provider), _ec2_attrs)

    def __init__(self, config):
        self.config = self._init_config(config)
        self.driver = self._create_driver()

    def create_node(self):
        image = self.driver.get_image(self.config['ami_id'])
        size = self._get_size()

        extra_args = {}
        if 'security_group_names' in self.config:
            extra_args['ex_securitygroup'] = self.config['security_group_names']

        node = self.driver.create_node(name='yabi-dynbe-instance',
                                       image=image, size=size,
                                       ex_keyname=self.config['keypair_name'],
                                       **extra_args)

        # TODO this code should go to is_node_ready
        # node_id will be set by create_node
        # ip_address will be set by is_node_ready
        result = self.driver.wait_until_running((node,), timeout=1200)
        if len(result) == 0:
            # TODO wrong type but this code will go away anyways
            raise StandardError("Node '%s' still not running!", node.id)
        node, ip_addresses = result[0]

        return CloudInstance(node.id, ip_addresses)

    def is_node_ready(self, instance_handle):
        pass

    def destroy_node(self, instance_handle):
        node = self._find_node(node_id=instance_handle)
        node.destroy()

    def _init_config(self, config):
        missing = filter(lambda x: x not in config, self.MANDATORY_CONFIG_KEYS)
        if len(missing) > 0:
            raise IncorrectConfigurationError(
                "The following mandatory keys are missing: %s" % ", ".join(missing))

        return config

    def _create_driver(self):
        region = self.config['region']
        if region not in self.VALID_REGIONS:
            raise IncorrectConfigurationError("Invalid AWS region '%s'" % region)
        cls = get_driver(region)

        return cls(self.config['access_id'], self.config['secret_key'])

    def _get_size(self):
        all_sizes = self.driver.list_sizes()
        mysize_or_empty = filter(lambda s: s.id == self.config['size_id'], all_sizes)
        if len(mysize_or_empty) == 0:
            raise IncorrectConfigurationError("Invalid size_id '%s'" % self.config['size_id'])
        return mysize_or_empty[0]

    def _find_node(self, node_id):
        def matches_id(node):
            return node.id == node_id
        ournode_or_empty = filter(matches_id, self.driver.list_nodes())
        if len(ournode_or_empty) == 0:
            # TODO proper type
            raise StandardError("Node '%s' not found", node_id)
        return ournode_or_empty[0]
