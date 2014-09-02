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
