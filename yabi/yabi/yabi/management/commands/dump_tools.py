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

import sys
import json
from optparse import make_option

from django.core.management.base import NoArgsCommand

from ...models import Tool


class Command(NoArgsCommand):
    help = "Outputs all tools in JSON format."
    option_list = NoArgsCommand.option_list + (
        make_option('--outfile', '-o',
                    dest='outfile',
                    default="-",
                    help="Output file"),
    )

    def handle(self, *args, **options):
        if options["outfile"] == "-":
            outfile = sys.stdout
        else:
            outfile = open(options["outfile"], "w")
        dump_tools(outfile)


def dump_tools(outfile=sys.stdout):
    all_tools = map(safe_tool_dict, Tool.objects.order_by("id"))
    all_tools = map(filter_backend_stuff, all_tools)
    all_tools = map(deserialize_maybe, all_tools)
    json.dump(all_tools, outfile, indent=2, sort_keys=True)
    outfile.write("\n")


def safe_tool_dict(tool):
    try:
        return tool.tool_dict()
    except ValueError:
        return {}


def filter_backend_stuff(backend_dict):
    for key in ("backend",):
        if key in backend_dict:
            del backend_dict[key]
    return backend_dict


def deserialize_maybe(backend_dict):
    for plist in backend_dict.get("parameter_list", []):
        if isinstance(plist.get("possible_values", None), basestring) and plist["possible_values"]:
            try:
                plist["possible_values"] = json.loads(plist["possible_values"])
            except ValueError:
                pass
    return backend_dict
