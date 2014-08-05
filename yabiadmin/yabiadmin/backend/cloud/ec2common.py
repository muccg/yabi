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
from libcloud.common.types import LibcloudError
from libcloud.compute.providers import get_driver
from libcloud.compute.drivers.ec2 import VALID_EC2_REGIONS

from .handler import CloudHandler
from .exceptions import IncorrectConfigurationError, CloudError


logger = logging.getLogger(__name__)


class EC2Base(CloudHandler):
    """Class to be mixed in into the ec2 and ec2 spot handlers."""

    INSTANCE_NAME = 'yabi-dynbe-instance'
    MANDATORY_CONFIG_KEYS = (
        'access_id', 'secret_key', 'region', 'size_id', 'ami_id', 'keypair_name')
    # In addition accepts
    # 'security_group_names': [
    #       "default", "ssh", "proxied", "rdsaccess" ]

    def __init__(self, config):
        self.config = self._init_config(config)
        self.driver = self._create_driver()

    def _handle_to_instance_id(self, instance_handle):
        raise NotImplementedError()

    def fetch_ip_address(self, instance_handle):
        instance_id = self._handle_to_instance_id(instance_handle)
        return self._fetch_ip_address(instance_id)

    def destroy_node(self, instance_handle):
        instance_id = self._handle_to_instance_id(instance_handle)
        node = self._find_node(node_id=instance_id)
        node.destroy()

    def _is_node_running(self, instance_id):
        TIMEOUT = 1
        node = self._find_node(node_id=instance_id)
        try:
            # We want to try just once, no retries
            # Therefore setting both wait_period and timeout to the same value
            self.driver.wait_until_running((node,),
                                           wait_period=TIMEOUT, timeout=TIMEOUT)

            return True

        except LibcloudError as e:
            if e.value.startswith('Timed out after %s seconds' % TIMEOUT):
                return False
            else:
                raise

    def _fetch_ip_address(self, instance_id):
        node = self._find_node(node_id=instance_id)
        if len(node.public_ips) > 0:
            return node.public_ips[0]

    def _init_config(self, config):
        missing = filter(lambda x: x not in config, self.MANDATORY_CONFIG_KEYS)
        if len(missing) > 0:
            raise IncorrectConfigurationError(
                "The following mandatory keys are missing: %s" % ", ".join(missing))

        return config

    def _create_driver(self):
        region = self.config['region']
        if region not in VALID_EC2_REGIONS:
            raise IncorrectConfigurationError("Invalid AWS region '%s'" % region)

        cls = get_driver(self._region_to_provider(region))

        return cls(self.config['access_id'], self.config['secret_key'])

    def _get_size(self):
        all_sizes = self.driver.list_sizes()
        mysize_or_empty = filter(lambda s: s.id == self.config['size_id'], all_sizes)
        if len(mysize_or_empty) == 0:
            raise IncorrectConfigurationError("Invalid size_id '%s'" % self.config['size_id'])
        return mysize_or_empty[0]

    def _find_node(self, node_id):
        ournode_or_empty = self.driver.list_nodes(ex_node_ids=(node_id,))
        if len(ournode_or_empty) == 0:
            raise CloudError("Node '%s' not found", node_id)
        return ournode_or_empty[0]
