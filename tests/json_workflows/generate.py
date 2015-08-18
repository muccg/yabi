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

from __future__ import print_function
import sys

PRE = """
{
    "name": "hostname",
    "tags": [],
    "jobs": [{"""

HOSTNAME = """
            "toolName":"hostname",
            "backendName":"Local Execution",
            "jobId":%s,
            "valid":true,
            "parameterList":{
                "parameter":[]
            }
"""

POST = """        }]
}
"""

def hostname(how_many):
    hostnames = HOSTNAME % 1
    i = 2
    while i <= how_many:
        hostnames = (" " * 8 + "},{").join([hostnames, HOSTNAME % i])
        i += 1
    print("".join([PRE, hostnames, POST]))

def main():
    count = 1
    if len(sys.argv) == 2:
        count = int(sys.argv[1])
    hostname(count)

if __name__ == "__main__":
    main()
