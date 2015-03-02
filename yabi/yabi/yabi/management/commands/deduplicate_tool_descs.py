from django.core.management.base import NoArgsCommand
from optparse import make_option

from ...models import Tool, ToolDesc
from ...migrationutils import deduplicate_tool_descs


class Command(NoArgsCommand):
    help = "Removes ToolDesc objects which are the same."
    option_list = NoArgsCommand.option_list + (
        make_option('--dry-run', '-n',
                    action='store_true',
                    dest='dry_run',
                    default=False,
                    help="Don't save changes to database"),
    )

    def handle(self, *args, **options):
        deduplicate_tool_descs(Tool, ToolDesc, options['dry_run'])
