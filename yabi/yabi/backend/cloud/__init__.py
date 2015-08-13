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

from .exceptions import IncorrectConfigurationError
from .ec2 import EC2Handler
from .ec2spot import EC2SpotHandler
from nova import NovaHandler


handler_registry = {
    'ec2': EC2Handler,
    'ec2spot': EC2SpotHandler,
    'nova': NovaHandler,
}


# Convenience methods for easier usage and also dealing with the
# instance <-> node terminology difference

def start_up_instance(config):
    handler = _create_handler_from_config(config)
    instance_handle = handler.create_node()

    return instance_handle


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
