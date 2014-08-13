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

from .ec2base import EC2Base


logger = logging.getLogger(__name__)


class EC2Handler(EC2Base):

    def __init__(self, config):
        EC2Base.__init__(self, config)

    def create_node(self):
        image = self.driver.get_image(self.config['ami_id'])
        size = self._get_size()

        extra_args = {}
        if 'security_group_names' in self.config:
            extra_args['ex_securitygroup'] = self.config['security_group_names']

        node = self.driver.create_node(name=self.INSTANCE_NAME,
                                       image=image, size=size,
                                       ex_keyname=self.config['keypair_name'],
                                       **extra_args)

        return node.id

    def is_node_ready(self, instance_handle):
        if self._is_node_running(instance_handle):
            return instance_handle

        return None

    def _handle_to_instance_id(self, instance_handle):
        return instance_handle

    def _region_to_provider(self, region):
        prefixed = "ec2-%s" % region

        return prefixed.replace("-", "_")
