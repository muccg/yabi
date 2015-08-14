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
from libcloud.compute.drivers.ec2 import VALID_EC2_REGIONS

from .handler import LibcloudBaseHandler
from .exceptions import IncorrectConfigurationError


logger = logging.getLogger(__name__)


class EC2Base(LibcloudBaseHandler):
    """Base class for ec2 and ec2 spot handlers."""

    MANDATORY_CONFIG_KEYS = (
        'access_id', 'secret_key', 'region', 'size_id', 'ami_id', 'keypair_name')
    # In addition accepts
    # 'security_group_names': [
    #       "default", "ssh", "proxied", "rdsaccess" ]

    def _create_driver(self):
        region = self.config['region']
        if region not in VALID_EC2_REGIONS:
            raise IncorrectConfigurationError("Invalid AWS region '%s'" % region)

        cls = get_driver(self._region_to_provider(region))

        return cls(self.config['access_id'], self.config['secret_key'])
