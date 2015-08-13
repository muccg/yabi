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

from .ec2base import EC2Base


logger = logging.getLogger(__name__)


class EC2Handler(EC2Base):

    def __init__(self, config):
        EC2Base.__init__(self, config)

    def create_node(self):
        image = self.driver.get_image(self.config['ami_id'])
        size = self._get_size_by_id(config_key='size_id')

        extra_args = {}
        if 'security_group_names' in self.config:
            extra_args['ex_securitygroup'] = self.config['security_group_names']

        node = self.driver.create_node(name=self.INSTANCE_NAME,
                                       image=image, size=size,
                                       ex_keyname=self.config['keypair_name'],
                                       **extra_args)

        return node.id

    def _region_to_provider(self, region):
        prefixed = "ec2-%s" % region

        return prefixed.replace("-", "_")
