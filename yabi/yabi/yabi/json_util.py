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

import datetime

import logging
logger = logging.getLogger(__name__)


def makeJsonFriendly(data):
    '''Will traverse a dict or list compound data struct and
    make any datetime.datetime fields json friendly
    '''

    try:
        if isinstance(data, list):
            for e in data:
                e = makeJsonFriendly(e)

        elif isinstance(data, dict):
            for key in data.keys():
                data[key] = makeJsonFriendly(data[key])

        elif isinstance(data, datetime.datetime):
            return str(data)

    except Exception as e:
        logger.critical("makeJsonFriendly encountered an error: %s" % str(e))
        raise

    return data
