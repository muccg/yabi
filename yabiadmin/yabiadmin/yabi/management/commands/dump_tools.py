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
