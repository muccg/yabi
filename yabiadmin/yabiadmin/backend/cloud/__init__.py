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
from .exceptions import IncorrectConfigurationError
from .ec2 import EC2Handler
from .ec2spot import EC2SpotHandler


handler_registry = {
    'ec2': EC2Handler,
    'ec2spot': EC2SpotHandler,
}


# Convenience methods for easier usage and also dealing with the
# instance <-> node terminology difference

def start_up_instance(config):
    handler = _create_handler_from_config(config)
    node = handler.create_node()

    return node


def is_instance_ready(instance_handle, config):
    handler = _create_handler_from_config(config)

    return handler.is_node_ready(instance_handle)


def fetch_ip_address(instance_handle, config):
    handler = _create_handler_from_config(config)

    return handler.fetch_ip_address(instance_handle)


def destroy_instance(instance_handle, config):
    handler = _create_handler_from_config(config)

    handler.destroy_node(instance_handle)


def _create_handler_from_config(config):
    instance_class = config.get('instance_class')
    if instance_class is None:
        raise IncorrectConfigurationError("'instance_class' missing from configuration.")
    cls = _get_handler_class(instance_class)

    return cls(config=config)


def _get_handler_class(instance_class):
    handler = handler_registry.get(instance_class)
    if handler is None:
        raise IncorrectConfigurationError("Unknown 'instance_class' '%s'.", instance_class)

    return handler
