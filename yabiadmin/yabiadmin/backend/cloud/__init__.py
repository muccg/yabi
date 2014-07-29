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
from cloudseeder import InstanceHandle, InstanceConfig, CloudSeeder
from .exceptions import IncorrectConfigurationError
from .ec2 import EC2Handler
from .ec2spot import EC2SpotHandler


logger = logging.getLogger(__name__)


registry = {
        'ec2': EC2Handler,
        'ec2spot': EC2SpotHandler,
    }


def start_up_instance(configuration):
    config = InstanceConfig("yabi_config", configuration)
    node = create_node(config)
    return node
    seeder = CloudSeeder()
    instance = seeder.instance(config)
    instance.start()

    return instance


def destroy_instance(handle, configuration):
    seeder = CloudSeeder()
    config = InstanceConfig("yabi_config", configuration)
    handle = InstanceHandle.from_json(handle)
    instance = seeder.get_instance(handle, config=config)
    instance.destroy()


def create_node(config):
    instance_type = config.get('instance_type')
    if instance_type is None:
        raise IncorrectConfigurationError("'instance_type' missing from configuration")
    handler = get_handler(instance_type)
    node = handler.create_node(config)

    return node


def get_handler(instance_type):
    handler= registry.get(instance_type)
    if handler is None:
        raise IncorrectConfigurationError("Unknown 'instance_type' '%s'", instance_type)

    return handler
