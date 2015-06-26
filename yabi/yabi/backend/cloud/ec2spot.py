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

from collections import namedtuple
import logging
import json
from ccglibcloud.ec2spot import set_spot_drivers

from .ec2base import EC2Base
from .exceptions import CloudError


logger = logging.getLogger(__name__)


# Register all the EC2 Spot drivers from ccglibcloud.ec2spot
set_spot_drivers()


class InvalidSpotInstanceRequestID(CloudError):
    pass


class Handle(namedtuple('HandleBase', ['spot_req_id', 'instance_id'])):
    @classmethod
    def from_json(cls, json_data):
        return Handle(**json.loads(json_data))

    def from_handle(self, instance_id):
        return self._replace(instance_id=instance_id)

    @property
    def has_instance_id(self):
        return self.instance_id is not None

    def to_json(self):
        return json.dumps(self._asdict())


class EC2SpotHandler(EC2Base):
    MANDATORY_CONFIG_KEYS = EC2Base.MANDATORY_CONFIG_KEYS + ('spot_price',)

    def create_node(self):
        image = self.driver.get_image(self.config['ami_id'])
        size = self._get_size_by_id(config_key='size_id')

        extra_args = {}
        if 'security_group_names' in self.config:
            extra_args['security_groups'] = self.config['security_group_names']

        spot_req = self.driver.ex_request_spot_instances(
            spot_price=self.config['spot_price'], image=image, size=size,
            keyname=self.config['keypair_name'],
            **extra_args)
        logger.info("Created spot request %s", spot_req)

        return Handle(spot_req.id, instance_id=None).to_json()

    def is_node_ready(self, instance_handle):
        handle = Handle.from_json(instance_handle)
        instance_id = handle.instance_id

        # Does the spot request has an instance already?
        if not instance_id:
            instance_id = self._get_spot_requests_instance_id(handle.spot_req_id)
            if instance_id is None:
                return None
            self._on_spot_request_got_instance(handle.spot_req_id, instance_id)

        # We have an instance, wait for the instance to be ready
        if self._is_node_running(instance_id):
            return handle.from_handle(instance_id=instance_id).to_json()

        return None

    def destroy_node(self, instance_handle):
        handle = Handle.from_json(instance_handle)
        spot_req = self._find_spot_request(spot_req_id=handle.spot_req_id)

        self.driver.ex_cancel_spot_instance_request(spot_req)

        # Spot request might not be fulfilled yet
        if handle.has_instance_id:
            EC2Base.destroy_node(self, instance_handle)

    def _handle_to_instance_id(self, instance_handle):
        handle = Handle.from_json(instance_handle)
        return handle.instance_id

    def _region_to_provider(self, region):
        prefixed = "ec2-spot-%s" % region

        return prefixed.replace("-", "_")

    def _find_spot_request(self, spot_req_id):
        try:
            ourspot_or_empty = self.driver.ex_list_spot_requests(spot_request_ids=(spot_req_id,))
            return ourspot_or_empty[0]
        except Exception as e:
            if 'InvalidSpotInstanceRequestID.NotFound' in str(e):
                raise InvalidSpotInstanceRequestID("Invalid spot instance request id '%s'", spot_req_id)
            raise

    def _on_spot_request_got_instance(self, spot_req_id, instance_id):
        logger.info("Your Spot request '%s' has an instance now: '%s'. Waiting for the instance to be ready.", spot_req_id, instance_id)
        # Set node name
        node = self._find_node(node_id=instance_id)
        self.driver.ex_create_tags(node, {"Name": self.INSTANCE_NAME})

    def _get_spot_requests_instance_id(self, spot_req_id):
        spot_request = self._find_spot_request(spot_req_id)
        instance_id = spot_request.instance_id

        if instance_id is None:
            logger.info("Spot requests '%s' status '%s'",
                        spot_request.id, spot_request.message)

        return instance_id
