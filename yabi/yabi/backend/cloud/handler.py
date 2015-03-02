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
from libcloud.common.types import LibcloudError
from .exceptions import IncorrectConfigurationError, CloudError


class CloudHandler(object):
    """Interface expected to be implemented by Handler classes.

    Handler classes are a facade to the libcloud API.

    The instance_handle used by some of the methods is Handler specific.
    Don't try to use code that interprets the handler in any ways. Just pass
    in the instance_handle you received from create_node and/or is_node_ready
    to the other methods that require it.
    """

    def __init__(self, config):
        """Expects a dictionary of handler specific configuration"""
        pass

    def create_node(self):
        """Initiates creation of a node based on the config passed into __init__.

        Return an instance handle."""
        raise NotImplementedError()

    def is_node_ready(self, instance_handle):
        """Is the node ready to use?

        Returns None if the instance isn't ready or the (new) instance handle if it is ready."""
        raise NotImplementedError()

    def fetch_ip_address(self, instance_handle):
        """Return the public IP address of the node."""
        raise NotImplementedError()

    def destroy_node(self, instance_handle):
        raise NotImplementedError()


class LibcloudBaseHandler(CloudHandler):
    """Common code among different libcloud handlers."""

    INSTANCE_NAME = 'yabi-dynbe-instance'

    def __init__(self, config):
        self.config = self._init_config(config)
        self.driver = self._create_driver()

    def _handle_to_instance_id(self, instance_handle):
        return instance_handle

    def fetch_ip_address(self, instance_handle):
        instance_id = self._handle_to_instance_id(instance_handle)
        return self._fetch_ip_address(instance_id)

    def destroy_node(self, instance_handle):
        instance_id = self._handle_to_instance_id(instance_handle)
        node = self._find_node(node_id=instance_id)
        node.destroy()

    def is_node_ready(self, instance_handle):
        if self._is_node_running(instance_handle):
            return instance_handle

        return None

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

    def _find_node(self, node_id):
        ournode_or_empty = filter(lambda n: n.id == node_id, self.driver.list_nodes())
        if len(ournode_or_empty) == 0:
            raise CloudError("Node '%s' not found", node_id)
        return ournode_or_empty[0]

    def _get_first(self, driver_method, finder_fn, config_key):
        value = self.config[config_key]
        all_matches = driver_method()
        mymatch_or_empty = filter(finder_fn(value), all_matches)
        if len(mymatch_or_empty) == 0:
            raise IncorrectConfigurationError("Invalid %s '%s'" % (config_key, value))

        return mymatch_or_empty[0]

    def _get_size_by_id(self, config_key):
        return self._get_first(self.driver.list_sizes, _by_id_finder, config_key)

    def _get_size_by_name(self, config_key):
        return self._get_first(self.driver.list_sizes, _by_name_finder, config_key)

    def _get_image_by_name(self, config_key):
        return self._get_first(self.driver.list_images, _by_name_finder, config_key)


def _by_id_finder(value):
    return lambda x: x.id == value


def _by_name_finder(value):
    return lambda x: x.name == value
